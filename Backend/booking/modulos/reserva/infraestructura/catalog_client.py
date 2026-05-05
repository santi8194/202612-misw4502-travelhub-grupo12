import datetime
import json
import os
from urllib import error, parse, request


def _normalize_inventory_date(value: str) -> str:
    # Catalog can return YYYY-MM-DD or an ISO datetime; keep only the date key.
    return value[:10]


class CatalogServiceClient:
    def __init__(self, base_url: str | None = None, timeout: int = 5):
        self.base_url = (base_url or os.getenv("CATALOG_SERVICE_URL") or self._default_base_url()).rstrip("/")
        self.timeout = timeout

    @staticmethod
    def _default_base_url() -> str:
        # Both Docker Compose and Kubernetes can reach catalog by its service name.
        if os.path.exists("/.dockerenv"):
            return "https://d1d660udfb1fc0.cloudfront.net/catalog"
        return "https://d1d660udfb1fc0.cloudfront.net/catalog"

    def _request_json(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Accept": "application/json"}

        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(url, data=data, headers=headers, method=method)

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload) if payload else {}
        except error.HTTPError as exc:
            payload = exc.read().decode("utf-8")
            try:
                detail = json.loads(payload)
            except json.JSONDecodeError:
                detail = {"error": payload or f"Catalog service HTTP {exc.code}"}
            raise ValueError(detail.get("error") or f"Catalog service HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise ValueError(f"No fue posible conectar con el servicio de catalog ({self.base_url})") from exc

    def get_property_by_category_id(self, id_categoria: str) -> dict:
        return self._request_json("GET", f"/properties/by-category/{parse.quote(id_categoria)}")

    def get_category_by_id(self, id_categoria: str) -> dict:
        return self._request_json("GET", f"/categories/{parse.quote(id_categoria)}")

    def get_categories_by_property_id(self, id_propiedad: str) -> dict:
        return self._request_json("GET", f"/properties/{parse.quote(id_propiedad)}/categories")

    def update_inventory(self, id_propiedad: str, id_categoria: str, inventory_item: dict) -> dict:
        payload = {
            "id_propiedad": id_propiedad,
            "id_categoria": id_categoria,
            "id_inventario": inventory_item["id_inventario"],
            "fecha": inventory_item["fecha"],
            "cupos_totales": inventory_item["cupos_totales"],
            "cupos_disponibles": inventory_item["cupos_disponibles"],
        }
        return self._request_json("PUT", f"/properties/{id_propiedad}/categories/{parse.quote(id_categoria)}/inventory", payload)

    def _build_inventory_updates(
        self,
        id_categoria: str,
        fecha_check_in: datetime.date,
        fecha_check_out: datetime.date,
        *,
        delta: int,
        require_availability: bool,
        cap_at_total: bool,
    ) -> tuple[str, list[dict]]:
        property_info = self.get_property_by_category_id(id_categoria)
        if property_info.get("error"):
            raise ValueError("La categoria no existe en catalog")

        category_info = self.get_category_by_id(id_categoria)
        if category_info.get("error"):
            raise ValueError("La categoria no existe en catalog")

        inventory_by_date = {
            _normalize_inventory_date(item["fecha"]): item
            for item in category_info.get("inventario", [])
        }

        updated_items: list[dict] = []
        current_date = fecha_check_in
        while current_date <= fecha_check_out:
            current_key = current_date.isoformat()
            inventory_item = inventory_by_date.get(current_key)
            if not inventory_item:
                raise ValueError(f"No existe inventario para la categoria en la fecha {current_key}")

            current_available = inventory_item["cupos_disponibles"]
            if require_availability and current_available <= 0:
                raise ValueError(f"No hay disponibilidad para la categoria en la fecha {current_key}")

            next_available = current_available + delta
            if cap_at_total:
                next_available = min(next_available, inventory_item["cupos_totales"])

            if next_available != current_available:
                updated_items.append(
                    {
                        **inventory_item,
                        "fecha": current_key,
                        "cupos_disponibles": next_available,
                        "id_propiedad": property_info["id_propiedad"],
                    }
                )

            current_date += datetime.timedelta(days=1)

        return property_info["id_propiedad"], updated_items

    def reserve_inventory(self, id_categoria: str, fecha_check_in: datetime.date, fecha_check_out: datetime.date) -> list[dict]:
        id_propiedad, updated_items = self._build_inventory_updates(
            id_categoria,
            fecha_check_in,
            fecha_check_out,
            delta=-1,
            require_availability=True,
            cap_at_total=False,
        )

        applied_updates: list[dict] = []
        try:
            for item in updated_items:
                self.update_inventory(id_propiedad, id_categoria, item)
                applied_updates.append(item)
        except Exception:
            self.restore_inventory(id_categoria, applied_updates)
            raise

        return [
            {
                **item,
                "cupos_disponibles": item["cupos_disponibles"] + 1,
            }
            for item in applied_updates
        ]

    def restore_inventory(self, id_categoria: str, original_items: list[dict]) -> None:
        for item in original_items:
            try:
                self.update_inventory(item["id_propiedad"], id_categoria, item)
            except Exception:
                continue

    def release_inventory(self, id_categoria: str, fecha_check_in: datetime.date, fecha_check_out: datetime.date) -> None:
        id_propiedad, updated_items = self._build_inventory_updates(
            id_categoria,
            fecha_check_in,
            fecha_check_out,
            delta=1,
            require_availability=False,
            cap_at_total=True,
        )

        errors: list[tuple[str, Exception]] = []
        for item in updated_items:
            try:
                self.update_inventory(id_propiedad, id_categoria, item)
            except Exception as exc:
                errors.append((item["fecha"], exc))

        if errors:
            failed_dates = ", ".join(fecha for fecha, _ in errors)
            raise ValueError(
                f"No fue posible liberar inventario para todas las fechas: {failed_dates}"
            )
