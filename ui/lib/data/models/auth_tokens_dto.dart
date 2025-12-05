import 'package:divvy_api_client/divvy_api_client.dart';

import '../../domain/entities/auth_tokens.dart';

/// Data Transfer Object for converting API [TokenResponse] to domain [AuthTokens].
class AuthTokensDto {
  /// Converts an API [TokenResponse] to a domain [AuthTokens].
  static AuthTokens fromApiModel(TokenResponse response) {
    return AuthTokens(
      accessToken: response.accessToken,
      refreshToken: response.refreshToken,
      expiresIn: response.expiresIn,
      tokenType: response.tokenType,
      scope: response.scope,
    );
  }
}
