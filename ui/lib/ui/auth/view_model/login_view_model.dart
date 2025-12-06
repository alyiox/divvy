import 'package:flutter/foundation.dart';

import '../../../core/common/result/result.dart';
import '../../../core/services/token_storage_service.dart';
import '../../../domain/repositories/auth_repository.dart';

/// ViewModel for managing login state and business logic.
class LoginViewModel extends ChangeNotifier {
  final AuthRepository _authRepository;
  final TokenStorageService _tokenStorage;

  LoginViewModel({required AuthRepository authRepository, required TokenStorageService tokenStorage})
    : _authRepository = authRepository,
      _tokenStorage = tokenStorage;

  bool _isLoading = false;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// Attempts to login with the provided email and password.
  /// Returns true if login was successful, false otherwise.
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _authRepository.login(email, password);

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
