import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../view_models/login_view_model.dart';
import '../widgets/custom_text_field.dart';

class LoginView extends StatelessWidget {
  const LoginView({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final viewModel = context.watch<LoginViewModel>();

    return Scaffold(
      backgroundColor: Colors.grey[100],
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: viewModel.formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  l10n.loginTitle,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: Colors.blue[800],
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 32),
                CustomTextField(
                  labelText: l10n.emailLabel,
                  onChanged: viewModel.setEmail,
                  validator: (value) =>
                      (value == null || value.isEmpty) ? l10n.emailLabel : null,
                ),
                CustomTextField(
                  labelText: l10n.passwordLabel,
                  obscureText: true,
                  onChanged: viewModel.setPassword,
                  validator: (value) => (value == null || value.isEmpty)
                      ? l10n.passwordLabel
                      : null,
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: viewModel.isLoading
                        ? null
                        : () async {
                            if (await viewModel.login()) {
                              if (context.mounted) {
                                Navigator.pushReplacementNamed(
                                  context,
                                  '/home',
                                );
                              }
                            }
                          },
                    style: ElevatedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: viewModel.isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : Text(l10n.loginButton),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(l10n.noAccountText),
                    GestureDetector(
                      onTap: () => Navigator.pushNamed(context, '/register'),
                      child: Text(
                        l10n.registerLink,
                        style: const TextStyle(
                          color: Colors.blue,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
