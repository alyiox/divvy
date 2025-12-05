import 'package:divvy_api_client/divvy_api_client.dart';
import 'package:get_it/get_it.dart';

import '../core/services/token_storage_service.dart';
import '../data/repositories/auth_repository_impl.dart';
import '../data/sources/remote_auth_data_source.dart';
import '../domain/repositories/auth_repository.dart';
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
}

void _configureRepositories() {
  it.registerSingleton<AuthRepository>(AuthRepositoryImpl(remoteAuthDataSource: it<RemoteAuthDataSource>()));
}

void _configurePresentations() {}
