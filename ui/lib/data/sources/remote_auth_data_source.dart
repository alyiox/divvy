import 'package:dio/dio.dart';
import 'package:divvy_api_client/divvy_api_client.dart';

import '../../core/common/result/result.dart';
import '../../domain/entities/auth_tokens.dart';
import '../models/auth_tokens_dto.dart';

class RemoteAuthDataSource {
  final DivvyApiClient apiClient;

  RemoteAuthDataSource({required this.apiClient});

  Future<Result<AuthTokens, Exception>> login(String email, String password) async {
    try {
      final response = await apiClient.getAuthenticationApi().tokenApiV1AuthTokenPost(
        grantType: 'password',
        username: email,
        password: password,
      );

      if (response.data == null) {
        return Result.error(Exception('Login response data is null'));
      }

      return Result.ok(AuthTokensDto.fromApiModel(response.data!));
    } on DioException catch (e) {
      return Result.error(Exception('Failed to login: ${e.message}'));
    } catch (e) {
      return Result.error(Exception('Unexpected error during login: $e'));
    }
  }

  Future<Result<AuthTokens, Exception>> register(String? name, String email, String password) async {
    try {
      final registerRequest = RegisterRequestBuilder()
        ..email = email
        ..name = name ?? email.split('@').first
        ..password = password;

      final response = await apiClient.getAuthenticationApi().registerApiV1AuthRegisterPost(
        registerRequest: registerRequest.build(),
      );

      if (response.data == null) {
        return Result.error(Exception('Register response data is null'));
      }

      return Result.ok(AuthTokensDto.fromApiModel(response.data!));
    } on DioException catch (e) {
      return Result.error(Exception('Failed to register: ${e.message}'));
    } catch (e) {
      return Result.error(Exception('Unexpected error during registration: $e'));
    }
  }

  Future<Result<AuthTokens, Exception>> refreshTokens(String refreshToken) async {
    try {
      final response = await apiClient.getAuthenticationApi().tokenApiV1AuthTokenPost(
        grantType: 'refresh_token',
        refreshToken: refreshToken,
      );

      if (response.data == null) {
        return Result.error(Exception('Token refresh response data is null'));
      }

      return Result.ok(AuthTokensDto.fromApiModel(response.data!));
    } on DioException catch (e) {
      return Result.error(Exception('Failed to refresh token: ${e.message}'));
    } catch (e) {
      return Result.error(Exception('Unexpected error during token refresh: $e'));
    }
  }
}
