/// Domain entity representing authentication tokens.
class AuthTokens {
  final String accessToken;
  final String refreshToken;
  final int expiresIn;
  final String? tokenType;
  final String? scope;

  const AuthTokens({
    required this.accessToken,
    required this.refreshToken,
    required this.expiresIn,
    this.tokenType,
    this.scope,
  });

  AuthTokens copyWith({
    String? accessToken,
    String? refreshToken,
    int? expiresIn,
    String? tokenType,
    String? scope,
  }) {
    return AuthTokens(
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      expiresIn: expiresIn ?? this.expiresIn,
      tokenType: tokenType ?? this.tokenType,
      scope: scope ?? this.scope,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AuthTokens &&
          runtimeType == other.runtimeType &&
          accessToken == other.accessToken &&
          refreshToken == other.refreshToken &&
          expiresIn == other.expiresIn &&
          tokenType == other.tokenType &&
          scope == other.scope;

  @override
  int get hashCode => Object.hash(accessToken, refreshToken, expiresIn, tokenType, scope);

  @override
  String toString() =>
      'AuthTokens(accessToken: ${accessToken.substring(0, accessToken.length > 10 ? 10 : accessToken.length)}..., refreshToken: ${refreshToken.substring(0, refreshToken.length > 10 ? 10 : refreshToken.length)}..., expiresIn: $expiresIn)';
}
