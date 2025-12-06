import 'package:flutter/foundation.dart';

import '../../../core/common/result/result.dart';
import '../../../core/services/token_storage_service.dart';
import '../../../domain/repositories/auth_repository.dart';

/// ViewModel for managing registration state and business logic.
class RegisterViewModel extends ChangeNotifier {
  final AuthRepository _authRepository;
  final TokenStorageService _tokenStorage;

  RegisterViewModel({required AuthRepository authRepository, required TokenStorageService tokenStorage})
    : _authRepository = authRepository,
      _tokenStorage = tokenStorage;

  bool _isLoading = false;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// Attempts to register a new user with the provided information.
  /// Returns true if registration was successful, false otherwise.
  Future<bool> register(String? name, String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _authRepository.register(name, email, password);

      switch (result) {
        case Ok(:final value):
          await _tokenStorage.saveTokens(value.accessToken, value.refreshToken);
          _isLoading = false;
          _errorMessage = null;
          notifyListeners();
          return true;

        case Error(:final error):
          _isLoading = false;
          _errorMessage = error.toString().replaceFirst('Exception: ', '');
          notifyListeners();
          return false;
      }
    } catch (e) {
      _isLoading = false;
      _errorMessage = 'An unexpected error occurred: ${e.toString()}';
      notifyListeners();
      return false;
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
