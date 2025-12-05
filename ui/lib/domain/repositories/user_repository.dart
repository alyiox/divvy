import '../../core/common/result/result.dart';
import '../entities/user_profile.dart';

abstract class UserRepository {
  Future<Result<UserProfile, Exception>> getCurrentUser();
}
