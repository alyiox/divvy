/// A sealed class representing the result of an operation that can either succeed or fail.
///
/// Provides type-safe error handling without exceptions. Use pattern matching for exhaustive handling.
///
/// Example:
/// ```dart
/// Result<int, FormatException> divide(int a, int b) {
///   if (b == 0) return Result.error(FormatException('Cannot divide by zero'));
///   return Result.ok(a ~/ b);
/// }
///
/// final result = divide(10, 2);
/// switch (result) {
///   case Ok(:final value): print('Result: $value');
///   case Error(:final error): print('Error: $error');
/// }
/// ```
sealed class Result<T, E extends Exception> {
  const Result();

  /// Creates a successful result containing the given [value].
  factory Result.ok(T value) = Ok<T, E>;

  /// Creates an error result containing the given [error].
  factory Result.error(E error) = Error<T, E>;
}

/// Represents a successful result containing a [value].
class Ok<T, E extends Exception> extends Result<T, E> {
  const Ok(this.value);

  /// The successful value returned from the operation.
  final T value;
}

/// Represents a failed result containing an [error].
class Error<T, E extends Exception> extends Result<T, E> {
  const Error(this.error);

  /// The error that occurred during the operation.
  final E error;
}
