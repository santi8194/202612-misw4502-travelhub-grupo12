# Tutorial Básico de Dart

Dart es el lenguaje de programación utilizado para crear aplicaciones Flutter. Es un lenguaje optimizado para clientes, diseñado para aplicaciones rápidas en cualquier plataforma.

## 1. Punto de Entrada
Cada aplicación Dart comienza con la función `main()`.
```dart
void main() {
  print('¡Hola, Dart!');
}
```

## 2. Variables y Tipos de Datos
Dart es seguro en cuanto a tipos (type-safe) pero admite la inferencia de tipos mediante `var`.

```dart
void main() {
  // Inferencia de tipos
  var name = 'Birdle'; 
  
  // Tipos explícitos
  String description = 'Un juego de palabras';
  int year = 2024;
  double version = 1.0;
  bool isAwesome = true;

  // Final y Const
  final now = DateTime.now(); // Se establece una vez en tiempo de ejecución
  const pi = 3.14; // Constante en tiempo de compilación
}
```

## 3. Colecciones
Dart tiene soporte integrado para Listas (Lists), Conjuntos (Sets) y Mapas (Maps).

```dart
void main() {
  // Listas (Arreglos)
  var list = ['aback', 'abase', 'abate'];
  
  // Mapas (Pares Clave-Valor)
  var colors = {
    'hit': 'green',
    'miss': 'grey',
    'partial': 'yellow',
  };
}
```

## 4. Funciones
Las funciones en Dart son objetos y pueden pasarse como argumentos (callbacks).

```dart
// Función estándar
int add(int a, int b) {
  return a + b;
}

// Sintaxis de flecha (para funciones de una sola línea)
int multiply(int a, int b) => a * b;

// Función de orden superior (recibe un callback)
void execute(void Function(String) callback) {
  callback('Hecho');
}
```

## 5. Clases y Objetos
Dart es un lenguaje orientado a objetos con clases y mixins.

```dart
class Word {
  final String text;

  // Constructor
  Word(this.text);

  // Constructor nombrado
  Word.empty() : text = '';

  void display() {
    print('La palabra es: $text');
  }
}

void main() {
  var myWord = Word('apple');
  myWord.display();
}
```

## 6. Programación Asíncrona
Dart utiliza `Future` y `Stream` para operaciones asíncronas, gestionadas mediante `async` y `await`.

```dart
Future<String> fetchData() async {
  // Simular retraso de red
  await Future.delayed(Duration(seconds: 2));
  return 'Datos de internet';
}

void main() async {
  print('Obteniendo...');
  String result = await fetchData();
  print(result);
}
```

## 7. Lógica y Control de Flujo
Dart admite `if/else` estándar, bucles `for` y potentes expresiones `switch`.

```dart
void checkType(HitType type) {
  var color = switch (type) {
    HitType.hit => 'green',
    HitType.partial => 'yellow',
    _ => 'white',
  };
  print(color);
}
```
