import '../../core/auth/token_refresher.dart';
import '../../core/common/result/result.dart';
import '../entities/auth_tokens.dart';

abstract class AuthRepository implements TokenRefresher {
  Future<Result<AuthTokens, Exception>> login(String email, String password);

  Future<Result<AuthTokens, Exception>> register(String? name, String email, String password);

  Future<Result<void, Exception>> logout(String refreshToken);
}
