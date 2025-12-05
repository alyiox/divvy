import 'package:dio/dio.dart';
import 'package:divvy_api_client/divvy_api_client.dart';

import '../../core/common/result/result.dart';
import '../../domain/entities/user_profile.dart';
import '../models/user_profile_dto.dart';

class RemoteUserDataSource {
  final DivvyApiClient apiClient;

  RemoteUserDataSource({required this.apiClient});

  Future<Result<UserProfile, Exception>> getUserProfile() async {
    try {
      final response = await apiClient.getUserApi().getCurrentUserInfoApiV1UserMeGet();

      if (response.data == null) {
        return Result.error(Exception('User profile response data is null'));
      }

      return Result.ok(UserProfileDto.fromApiModel(response.data!));
    } on DioException catch (e) {
      return Result.error(Exception('Failed to get user profile: ${e.message}'));
    } catch (e) {
      return Result.error(Exception('Unexpected error getting user profile: $e'));
    }
  }
}
