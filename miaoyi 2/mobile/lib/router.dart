import 'package:go_router/go_router.dart';

import 'api/api_client.dart';
import 'chat/chat_screen.dart';
import 'scan/scan_screen.dart';

GoRouter buildRouter(ApiClient api) => GoRouter(routes: [
      GoRoute(path: '/', builder: (_, __) => const ChatScreen()),
      GoRoute(path: '/scan', builder: (_, __) => ScanScreen(api: api)),
    ]);
