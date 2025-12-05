import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Service for managing authentication tokens in secure storage.
class TokenStorageService {
  static const String _accessTokenKey = 'divvy_access_token';
  static const String _refreshTokenKey = 'divvy_refresh_token';

  final FlutterSecureStorage _storage = FlutterSecureStorage();

  /// Saves both access and refresh tokens.
  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await Future.wait([
      _storage.write(key: _accessTokenKey, value: accessToken),
      _storage.write(key: _refreshTokenKey, value: refreshToken),
    ]);
  }

  /// Retrieves the access token.
  Future<String?> getAccessToken() => _storage.read(key: _accessTokenKey);

  /// Retrieves the refresh token.
  Future<String?> getRefreshToken() => _storage.read(key: _refreshTokenKey);

  /// Clears all stored tokens.
  Future<void> clearTokens() async {
    await Future.wait([_storage.delete(key: _accessTokenKey), _storage.delete(key: _refreshTokenKey)]);
  }

  /// Checks if tokens are stored.
  Future<bool> hasTokens() async {
    final accessToken = await getAccessToken();
    final refreshToken = await getRefreshToken();
    return accessToken != null && refreshToken != null;
  }
}
