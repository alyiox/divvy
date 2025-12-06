import 'package:flutter/material.dart';

import 'di/injection_container.dart';
import 'ui/auth/widgets/welcome_screen.dart';
import 'ui/home/widgets/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  configureDependencies();

  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Divvy',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue), useMaterial3: true),
      home: const WelcomeScreen(),
      routes: {'/home': (context) => const HomeScreen()},
    );
  }
}
