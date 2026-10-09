import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'api/api_client.dart';
import 'chat/chat_bloc.dart';
import 'router.dart';

void main() => runApp(const MiaoyiApp());

class MiaoyiApp extends StatefulWidget {
  const MiaoyiApp({super.key});
  @override
  State<MiaoyiApp> createState() => _MiaoyiAppState();
}

class _MiaoyiAppState extends State<MiaoyiApp> {
  // Replace the token provider with the Supabase session access token once sign-in is wired up.
  final _api = ApiClient();
  late final _router = buildRouter(_api);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => ChatBloc(_api),
      child: MaterialApp.router(
        title: 'Miaoyi',
        debugShowCheckedModeBanner: false,
        routerConfig: _router,
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2F6F5E), tertiary: const Color(0xFFB5362B)),
          scaffoldBackgroundColor: const Color(0xFFF6F8F5),
        ),
      ),
    );
  }
}
