import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/services/token_storage_service.dart';
import '../../../di/injection_container.dart';
import '../../../domain/repositories/auth_repository.dart';
import '../../auth/view_model/logout_view_model.dart';
import '../../auth/widgets/welcome_screen.dart';

/// Simple home screen widget.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => LogoutViewModel(authRepository: it<AuthRepository>(), tokenStorage: it<TokenStorageService>()),
      child: const _HomeScreenContent(),
    );
  }
}

class _HomeScreenContent extends StatelessWidget {
  const _HomeScreenContent();

  Future<void> _handleLogout(BuildContext context, LogoutViewModel viewModel) async {
    final success = await viewModel.logout();

    if (!success && viewModel.errorMessage != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(viewModel.errorMessage!), backgroundColor: Colors.red));
    }

    if (success) {
      Navigator.of(
        context,
      ).pushAndRemoveUntil(MaterialPageRoute(builder: (context) => const WelcomeScreen()), (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<LogoutViewModel>(
      builder: (context, viewModel, child) {
        return Scaffold(
          appBar: AppBar(title: const Text('Divvy')),
          body: Center(
            child: ElevatedButton.icon(
              onPressed: viewModel.isLoading ? null : () => _handleLogout(context, viewModel),
              icon: viewModel.isLoading
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.logout),
              label: const Text('Logout'),
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24)),
            ),
          ),
        );
      },
    );
  }
}
