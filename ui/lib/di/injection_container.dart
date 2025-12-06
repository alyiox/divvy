import 'package:divvy_api_client/divvy_api_client.dart';
import 'package:get_it/get_it.dart';

import '../core/services/token_storage_service.dart';
import '../data/repositories/index.dart';
import '../data/sources/index.dart';
import '../domain/repositories/index.dart';
import 'api_client_factory.dart';

final it = GetIt.instance;

void configureDependencies() {
  _configureCoreServices();
  _configureApiClients();
  _configureDataSources();
  _configureRepositories();
  _configurePresentations();
}

void _configureCoreServices() {
  it.registerSingleton<TokenStorageService>(TokenStorageService());
}

void _configureApiClients() {
  it.registerLazySingleton<DivvyApiClient>(() => ApiClientFactory.createPublicApiClient(), instanceName: 'public');

  it.registerLazySingleton(() {
    final tokenStorage = it<TokenStorageService>();
    final tokenRefresher = it<AuthRepository>();
    return ApiClientFactory.createAuthApiClient(tokenStorage: tokenStorage, tokenRefresher: tokenRefresher);
  }, instanceName: 'auth');
}

void _configureDataSources() {
  it.registerLazySingleton<RemoteAuthDataSource>(
    () => RemoteAuthDataSource(apiClient: it<DivvyApiClient>(instanceName: 'public')),
  );
  it.registerLazySingleton<RemoteUserDataSource>(
    () => RemoteUserDataSource(apiClient: it<DivvyApiClient>(instanceName: 'auth')),
  );
}

void _configureRepositories() {
  it.registerLazySingleton<AuthRepository>(() => AuthRepositoryImpl(remoteAuthDataSource: it<RemoteAuthDataSource>()));
  it.registerLazySingleton<UserRepository>(() => UserRepositoryImpl(remoteUserDataSource: it<RemoteUserDataSource>()));
}

void _configurePresentations() {}
