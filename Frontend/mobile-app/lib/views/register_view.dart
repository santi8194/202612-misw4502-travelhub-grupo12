import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../l10n/app_localizations.dart';
import '../view_models/register_view_model.dart';
import '../widgets/custom_text_field.dart';

class RegisterView extends StatelessWidget {
  const RegisterView({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final viewModel = context.watch<RegisterViewModel>();

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: Text(l10n.registerTitle),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.blue),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: viewModel.formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  l10n.registerTitle,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    color: Colors.blue[800],
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 32),
                CustomTextField(
                  labelText: l10n.fullNameLabel,
                  onChanged: viewModel.setFullName,
                  validator: (value) => (value == null || value.isEmpty)
                      ? l10n.fullNameLabel
                      : null,
                ),
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
                CustomTextField(
                  labelText: l10n.confirmPasswordLabel,
                  obscureText: true,
                  onChanged: viewModel.setConfirmPassword,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return l10n.confirmPasswordLabel;
                    }
                    if (value != viewModel.password) {
                      // Simple manual check
                      return "Passwords do not match";
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: viewModel.isLoading
                        ? null
                        : () async {
                            if (await viewModel.register()) {
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
                        : Text(l10n.registerButton),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(l10n.haveAccountText),
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Text(
                        l10n.loginLink,
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
