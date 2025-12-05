import '../../core/common/result/result.dart';
import '../../domain/entities/user_profile.dart';
import '../../domain/repositories/user_repository.dart';
import '../sources/remote_user_data_source.dart';

class UserRepositoryImpl extends UserRepository {
  final RemoteUserDataSource _remoteUserDataSource;

  UserRepositoryImpl({required RemoteUserDataSource remoteUserDataSource})
    : _remoteUserDataSource = remoteUserDataSource;

  @override
  Future<Result<UserProfile, Exception>> getCurrentUser() async {
    return _remoteUserDataSource.getUserProfile();
  }
}
