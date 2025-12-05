import 'package:dio/dio.dart';
import 'package:divvy_api_client/divvy_api_client.dart' show DivvyApiClient, standardSerializers;
import 'package:logger/logger.dart';

import '../config/app_config.dart';
import '../core/auth/token_refresher.dart';
import '../core/network/auth_interceptor.dart';
import '../core/services/token_storage_service.dart';

class ApiClientFactory {
  static DivvyApiClient createPublicApiClient() {
    final dio = _createBaseDio();
    return DivvyApiClient(dio: dio, serializers: standardSerializers);
  }

  static DivvyApiClient createAuthApiClient({
    required TokenStorageService tokenStorage,
    required TokenRefresher tokenRefresher,
  }) {
    final dio = _createBaseDio();
    dio.interceptors.add(AuthInterceptor(tokenStorage: tokenStorage, tokenRefresher: tokenRefresher));
    return DivvyApiClient(dio: dio, serializers: standardSerializers);
  }

  static Dio _createBaseDio() {
    final dio = Dio(BaseOptions(baseUrl: AppConfig.baseUrl));
    final logger = Logger();

    dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        requestHeader: true,
        responseHeader: true,
        error: true,
        logPrint: (object) => logger.d(object.toString()),
      ),
    );

    return dio;
  }
}
