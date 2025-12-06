import 'package:flutter/foundation.dart';

import '../../../core/common/result/result.dart';
import '../../../core/services/token_storage_service.dart';
import '../../../domain/repositories/auth_repository.dart';

/// ViewModel for managing logout state and business logic.
class LogoutViewModel extends ChangeNotifier {
  final AuthRepository _authRepository;
  final TokenStorageService _tokenStorage;

  LogoutViewModel({required AuthRepository authRepository, required TokenStorageService tokenStorage})
    : _authRepository = authRepository,
      _tokenStorage = tokenStorage;

  bool _isLoading = false;
  String? _errorMessage;

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  /// Logs out the user by revoking the refresh token on the server and clearing local tokens.
  /// Returns true if logout was successful, false otherwise.
  Future<bool> logout() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Get refresh token before clearing
      final refreshToken = await _tokenStorage.getRefreshToken();

      if (refreshToken != null) {
        // Revoke token on server
        final revokeResult = await _authRepository.logout(refreshToken);

        switch (revokeResult) {
          case Ok():
            // Token revoked successfully, now clear local storage
            await _tokenStorage.clearTokens();
            _isLoading = false;
            _errorMessage = null;
            notifyListeners();
            return true;

          case Error(:final error):
            // Even if revoke fails, clear local tokens for security
            await _tokenStorage.clearTokens();
            _isLoading = false;
            _errorMessage = error.toString().replaceFirst('Exception: ', '');
            notifyListeners();
            return false;
        }
      } else {
        // No refresh token found, just clear local storage
        await _tokenStorage.clearTokens();
        _isLoading = false;
        _errorMessage = null;
        notifyListeners();
        return true;
      }
    } catch (e) {
      // On any error, still clear local tokens for security
      await _tokenStorage.clearTokens();
      _isLoading = false;
      _errorMessage = 'An unexpected error occurred during logout: ${e.toString()}';
      notifyListeners();
      return false;
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
