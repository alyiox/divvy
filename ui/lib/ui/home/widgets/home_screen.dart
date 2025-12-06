import 'package:flutter/material.dart';

import '../../../core/services/token_storage_service.dart';
import '../../../di/injection_container.dart';
import '../../../domain/repositories/auth_repository.dart';
import '../../auth/view_model/logout_view_model.dart';
import '../../auth/widgets/welcome_screen.dart';

/// Simple home screen widget.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final LogoutViewModel _logoutViewModel;

  @override
  void initState() {
    super.initState();
    _logoutViewModel = LogoutViewModel(authRepository: it<AuthRepository>(), tokenStorage: it<TokenStorageService>());
    _logoutViewModel.addListener(_onLogoutViewModelChanged);
  }

  @override
  void dispose() {
    _logoutViewModel.removeListener(_onLogoutViewModelChanged);
    super.dispose();
  }

  void _onLogoutViewModelChanged() {
    if (_logoutViewModel.errorMessage != null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(_logoutViewModel.errorMessage!), backgroundColor: Colors.red));
    }
  }

  Future<void> _handleLogout() async {
    final success = await _logoutViewModel.logout();

    if (success && mounted) {
      Navigator.of(
        context,
      ).pushAndRemoveUntil(MaterialPageRoute(builder: (context) => const WelcomeScreen()), (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Divvy')),
      body: Center(
        child: ElevatedButton.icon(
          onPressed: _logoutViewModel.isLoading ? null : _handleLogout,
          icon: _logoutViewModel.isLoading
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
              : const Icon(Icons.logout),
          label: const Text('Logout'),
          style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24)),
        ),
      ),
    );
  }
}
