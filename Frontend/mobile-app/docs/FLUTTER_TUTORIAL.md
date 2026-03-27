# Tutorial de Fundamentos de Flutter

> Based on https://docs.flutter.dev/learn/pathway

Este tutorial cubre los conceptos principales del desarrollo con Flutter, desde la creación de tu primera aplicación hasta patrones avanzados de UI y gestión de estado.

## 1. Crear tu Primera Aplicación

Para crear un nuevo proyecto de Flutter desde la línea de comandos:

```bash
flutter create mi_app --empty
```

El punto de entrada de cada aplicación Flutter es la función `main()`, que llama a `runApp()` para adjuntar el widget raíz a la pantalla.

```dart
void main() {
  runApp(const MyApp());
}
```

### Hot Reload

El **Stateful Hot Reload** de Flutter te permite ver los cambios en el código en menos de un segundo sin perder el estado de la aplicación. Presiona `r` en la terminal o usa el botón de hot reload de tu IDE.

---

## 2. Fundamentos de los Widgets

Todo en Flutter es un **Widget**. Los widgets son descripciones declarativas de la interfaz de usuario (UI).

- **StatelessWidget**: Widgets inmutables que no cambian con el tiempo.
- **Método Build**: Cada widget debe implementar un método `build` que retorna otro widget.
- **Container**: Un widget versátil para dar estilo, añadir márgenes, rellenos (padding) y bordes mediante `BoxDecoration`.

```dart
class MiCelda extends StatelessWidget {
  final String etiqueta;
  const MiCelda(this.etiqueta, {super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.blue,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(etiqueta),
    );
  }
}
```

---

## 3. Layouts (Diseños)

Flutter utiliza una composición de widgets de diseño para organizar a los hijos:

- **Scaffold**: Proporciona la estructura visual básica de Material Design (AppBar, Body, FloatingActionButton).
- **Row & Column**: Organizan a los hijos horizontal o verticalmente. Usa la propiedad `spacing` para obtener espacios constantes.
- **Expanded**: Le indica a un hijo de un Row o Column que ocupe todo el espacio disponible restante.

---

## 4. Stateful Widgets

Cuando un widget necesita cambiar su apariencia en respuesta a la interacción del usuario o actualizaciones de datos, utiliza un `StatefulWidget`.

1.  **Clase State**: Mantiene los datos mutables.
2.  **setState()**: Indica al framework que el estado interno ha cambiado y que la UI necesita ser reconstruida.

```dart
class Contador extends StatefulWidget {
  @override
  State<Contador> createState() => _ContadorState();
}

class _ContadorState extends State<Contador> {
  int _cuenta = 0;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () => setState(() => _cuenta++),
      child: Text('Cuenta: $_cuenta'),
    );
  }
}
```

---

## 5. Entrada de Usuario (User Input)

- **TextField**: Captura la entrada de texto. Usa un `TextEditingController` para leer o limpiar el texto.
- **FocusNode**: Gestiona qué widget tiene el foco del teclado.
- **Callbacks**: Usa funciones pasadas como argumentos (ej. `onSubmitted`) para comunicar la entrada de vuelta a los widgets padres.

---

## 6. Animaciones Implícitas

Las animaciones implícitas son la forma más sencilla de añadir pulido. Widgets como `AnimatedContainer` animan automáticamente los cambios de propiedades (color, tamaño, etc.) durante una duración (`duration`) y curva (`curve`) especificadas.

---

## 7. Networking y Gestión de Estado (MVVM)

Para aplicaciones escalables, utiliza el patrón **Model-View-ViewModel (MVVM)**:

- **Model**: Lógica de datos y peticiones HTTP usando `async/await` y `jsonDecode`.
- **ViewModel**: Extiende de `ChangeNotifier`. Gestiona el estado de la app y llama a `notifyListeners()` cuando los datos cambian.
- **View**: Escucha al ViewModel usando `ListenableBuilder` para reconstruir la UI automáticamente.

```dart
// ViewModel
class ArticuloViewModel extends ChangeNotifier {
  bool cargando = false;

  Future<void> obtenerDatos() async {
    cargando = true;
    notifyListeners();
    // ... lógica de obtención ...
    cargando = false;
    notifyListeners();
  }
}

// View
ListenableBuilder(
  listenable: viewModel,
  builder: (context, child) {
    if (viewModel.cargando) return CircularProgressIndicator();
    return Text('Datos Cargados');
  },
)
```

---

## 8. UI Avanzada: Slivers y Desplazamiento

Los **Slivers** son widgets especializados para efectos de desplazamiento avanzados (cabeceras colapsables, paralaje).

- **CustomScrollView**: El widget padre que contiene una lista de slivers.
- **SliverList**: El equivalente en sliver de un ListView.
- **SliverToBoxAdapter**: Envuelve un widget normal para ser usado dentro de un CustomScrollView.

---

## 9. Navegación

Flutter utiliza un sistema de navegación basado en pilas:

- **Navigator.push()**: Añade una nueva pantalla a la pila.
- **Navigator.pop()**: Elimina la pantalla actual.
- **CupertinoPageRoute**: Proporciona transiciones nativas al estilo iOS.

---

## 10. Cómo funciona Flutter internamente

Flutter gestiona tres árboles para mantener el rendimiento de la UI:

1.  **Árbol de Widgets (Widget Tree)**: La configuración declarativa que escribes.
2.  **Árbol de Elementos (Element Tree)**: El "pegamento" que gestiona el ciclo de vida y enlaza los widgets con los objetos de renderizado.
3.  **Árbol de Objetos de Renderizado (RenderObject Tree)**: Gestiona el diseño real y el pintado de píxeles en la pantalla.

El **Motor de Flutter (Flutter Engine)** (escrito en C++) proporciona el soporte de renderizado de bajo nivel (usando Skia o Impeller) e interactúa con la plataforma anfitriona (Android/iOS).
