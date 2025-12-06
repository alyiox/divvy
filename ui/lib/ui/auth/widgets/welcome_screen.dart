import 'package:flutter/material.dart';

import 'login_screen.dart';
import 'register_screen.dart';

/// Welcome screen that allows users to choose between login and register.
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  void _navigateToLogin(BuildContext context) {
    Navigator.of(context).push(MaterialPageRoute(builder: (context) => const LoginScreen()));
  }

  void _navigateToRegister(BuildContext context) {
    Navigator.of(context).push(MaterialPageRoute(builder: (context) => const RegisterScreen()));
  }

  void _handleGoogleSignIn() {
    // TODO: Implement Google OAuth flow
  }

  void _handleMicrosoftSignIn() {
    // TODO: Implement Microsoft OAuth flow
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Icon(Icons.account_balance_wallet_outlined, size: 80, color: Colors.blue),
                const SizedBox(height: 32),
                const Text(
                  'Welcome to Divvy',
                  style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                const Text(
                  'Track and split shared expenses among groups, roommates, and shared households.',
                  style: TextStyle(fontSize: 16, color: Colors.grey),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 48),
                ElevatedButton.icon(
                  onPressed: _handleGoogleSignIn,
                  icon: const Icon(Icons.g_mobiledata, size: 24),
                  label: const Text('Continue with Google'),
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                ),
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  onPressed: _handleMicrosoftSignIn,
                  icon: const Icon(Icons.window, size: 24),
                  label: const Text('Continue with Microsoft'),
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                ),
                const SizedBox(height: 24),
                const Row(
                  children: [
                    Expanded(child: Divider()),
                    Padding(padding: EdgeInsets.symmetric(horizontal: 16), child: Text('OR')),
                    Expanded(child: Divider()),
                  ],
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () => _navigateToLogin(context),
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                  child: const Text('Sign In'),
                ),
                const SizedBox(height: 16),
                OutlinedButton(
                  onPressed: () => _navigateToRegister(context),
                  style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
                  child: const Text('Create Account'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
