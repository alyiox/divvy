import 'package:divvy_api_client/divvy_api_client.dart';

import '../../domain/entities/user_profile.dart';

/// Data Transfer Object for converting API [UserResponse] to domain [UserProfile].
class UserProfileDto {
  /// Converts an API [UserResponse] to a domain [UserProfile].
  static UserProfile fromApiModel(UserResponse response) {
    return UserProfile(
      id: response.id,
      email: response.email,
      name: response.name,
      avatar: response.avatar,
      isActive: response.isActive ?? true,
    );
  }
}
