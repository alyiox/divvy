import 'package:dio/dio.dart';

import '../auth/token_refresher.dart';
import '../common/result/result.dart';
import '../services/token_storage_service.dart';

class AuthInterceptor extends Interceptor {
  final TokenStorageService _tokenStorage;
  final TokenRefresher _tokenRefresher;
  bool _isRefreshing = false;

  AuthInterceptor({required TokenStorageService tokenStorage, required TokenRefresher tokenRefresher})
    : _tokenStorage = tokenStorage,
      _tokenRefresher = tokenRefresher;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final accessToken = await _tokenStorage.getAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401 && !err.requestOptions.path.contains('/token')) {
      final refreshToken = await _tokenStorage.getRefreshToken();
      if (refreshToken == null) {
        handler.reject(err);
        return;
      }

      // Prevent multiple simultaneous refresh attempts
      if (_isRefreshing) {
        handler.reject(err);
        return;
      }

      _isRefreshing = true;

      try {
        final result = await _tokenRefresher.refreshTokens(refreshToken);
        switch (result) {
          case Ok(:final value):
            await _tokenStorage.saveTokens(value.accessToken, value.refreshToken);

            // Retry the original request with new token
            final opts = err.requestOptions;
            opts.headers['Authorization'] = 'Bearer ${value.accessToken}';
            final response = await Dio().fetch(opts);
            handler.resolve(response);
            break;
          case Error():
            _isRefreshing = false;
            handler.reject(err);
            break;
        }
      } catch (e) {
        _isRefreshing = false;
        handler.reject(err);
      } finally {
        _isRefreshing = false;
      }
    } else {
      handler.next(err);
    }
  }
}
