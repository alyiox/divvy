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
  it.registerLazySingleton<DivvyApiClient>(() => ApiClientFactory.createPublicApiClient());

  it.registerLazySingleton(() {
    final tokenStorage = it<TokenStorageService>();
    final tokenRefresher = it<AuthRepository>();
    return ApiClientFactory.createAuthApiClient(tokenStorage: tokenStorage, tokenRefresher: tokenRefresher);
  });
}

void _configureDataSources() {
  DivvyApiClient publicApiClient = it<DivvyApiClient>(instanceName: 'public');
  it.registerSingleton<RemoteAuthDataSource>(RemoteAuthDataSource(apiClient: publicApiClient));
  it.registerSingleton<RemoteUserDataSource>(RemoteUserDataSource(apiClient: publicApiClient));
}

void _configureRepositories() {
  it.registerSingleton<AuthRepository>(AuthRepositoryImpl(remoteAuthDataSource: it<RemoteAuthDataSource>()));
  it.registerSingleton<UserRepository>(UserRepositoryImpl(remoteUserDataSource: it<RemoteUserDataSource>()));
}

void _configurePresentations() {}
