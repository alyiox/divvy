/// Domain entity representing user profile information.
class UserProfile {
  final int id;
  final String email;
  final String name;
  final String? avatar;
  final bool isActive;

  const UserProfile({required this.id, required this.email, required this.name, this.avatar, this.isActive = true});

  /// Creates a copy of this [UserProfile] with the given fields replaced.
  UserProfile copyWith({int? id, String? email, String? name, String? avatar, bool? isActive}) {
    return UserProfile(
      id: id ?? this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      avatar: avatar ?? this.avatar,
      isActive: isActive ?? this.isActive,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UserProfile &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          email == other.email &&
          name == other.name &&
          avatar == other.avatar &&
          isActive == other.isActive;

  @override
  int get hashCode => Object.hash(id, email, name, avatar, isActive);

  @override
  String toString() => 'UserProfile(id: $id, email: $email, name: $name, avatar: $avatar, isActive: $isActive)';
}
