import '../../core/common/result/result.dart';
import '../../domain/entities/auth_tokens.dart';

abstract class TokenRefresher {
  Future<Result<AuthTokens, Exception>> refreshTokens(String refreshToken);
}
