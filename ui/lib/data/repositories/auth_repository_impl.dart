import '../../core/common/result/result.dart';
import '../../domain/entities/auth_tokens.dart';
import '../../domain/repositories/auth_repository.dart';
import '../sources/remote_auth_data_source.dart';

class AuthRepositoryImpl extends AuthRepository {
  final RemoteAuthDataSource _remoteAuthDataSource;

  AuthRepositoryImpl({required RemoteAuthDataSource remoteAuthDataSource})
    : _remoteAuthDataSource = remoteAuthDataSource;

  @override
  Future<Result<AuthTokens, Exception>> login(String email, String password) async {
    return _remoteAuthDataSource.login(email, password);
  }

  @override
  Future<Result<AuthTokens, Exception>> register(String? name, String email, String password) async {
    return _remoteAuthDataSource.register(name, email, password);
  }

  @override
  Future<Result<AuthTokens, Exception>> refreshTokens(String refreshToken) async {
    return _remoteAuthDataSource.refreshTokens(refreshToken);
  }
}
