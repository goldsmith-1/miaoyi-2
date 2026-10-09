import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import 'chat_bloc.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _ctrl = TextEditingController();

  void _send() {
    final t = _ctrl.text.trim();
    if (t.isEmpty) return;
    context.read<ChatBloc>().add(Sent(t));
    _ctrl.clear();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Miaoyi 妙医'), actions: [
        IconButton(tooltip: 'Scan a label', icon: const Icon(Icons.document_scanner_outlined), onPressed: () => context.push('/scan')),
      ]),
      body: Column(children: [
        Container(
          width: double.infinity,
          color: theme.colorScheme.tertiaryContainer,
          padding: const EdgeInsets.all(8),
          child: const Text('General information only. Not a diagnosis or treatment. See a doctor for health concerns.', style: TextStyle(fontSize: 12)),
        ),
        Expanded(
          child: BlocBuilder<ChatBloc, ChatState>(builder: (context, s) {
            return ListView(padding: const EdgeInsets.all(12), children: [
              for (final m in s.messages)
                Align(
                  alignment: m.fromUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    constraints: const BoxConstraints(maxWidth: 520),
                    decoration: BoxDecoration(
                      color: m.fromUser ? theme.colorScheme.primaryContainer : Colors.white,
                      border: Border.all(color: Colors.black12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(m.text),
                      if (m.sources.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Text(m.sources.join('\n'), style: theme.textTheme.bodySmall),
                      ],
                    ]),
                  ),
                ),
              if (s.loading) const Padding(padding: EdgeInsets.all(12), child: LinearProgressIndicator()),
              if (s.error != null) Padding(padding: const EdgeInsets.all(8), child: Text(s.error!, style: TextStyle(color: theme.colorScheme.error))),
            ]);
          }),
        ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(8),
            child: Row(children: [
              Expanded(child: TextField(controller: _ctrl, minLines: 1, maxLines: 4, onSubmitted: (_) => _send(), decoration: const InputDecoration(hintText: 'Ask a health question', border: OutlineInputBorder()))),
              const SizedBox(width: 8),
              IconButton.filled(onPressed: _send, icon: const Icon(Icons.send)),
            ]),
          ),
        ),
      ]),
    );
  }
}
