import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../api/api_client.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key, required this.api});
  final ApiClient api;
  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final _picker = ImagePicker();
  bool _busy = false;
  Reply? _reply;
  String? _error;

  Future<void> _scan(ImageSource source) async {
    final f = await _picker.pickImage(source: source, maxWidth: 1600, imageQuality: 85);
    if (f == null) return;
    setState(() {
      _busy = true;
      _error = null;
      _reply = null;
    });
    try {
      final r = await widget.api.scan(await f.readAsBytes(), f.name, f.mimeType ?? 'image/jpeg');
      setState(() => _reply = r);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan a label')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        const Text('Photograph a medicine or ingredient label and get a plain-language explanation.'),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(child: FilledButton.icon(onPressed: _busy ? null : () => _scan(ImageSource.camera), icon: const Icon(Icons.photo_camera), label: const Text('Camera'))),
          const SizedBox(width: 12),
          Expanded(child: OutlinedButton.icon(onPressed: _busy ? null : () => _scan(ImageSource.gallery), icon: const Icon(Icons.photo_library), label: const Text('Gallery'))),
        ]),
        if (_busy) const Padding(padding: EdgeInsets.all(16), child: LinearProgressIndicator()),
        if (_error != null) Padding(padding: const EdgeInsets.only(top: 12), child: Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error))),
        if (_reply != null) ...[
          const SizedBox(height: 16),
          Text('Text found', style: Theme.of(context).textTheme.titleSmall),
          Text(_reply!.extractedText ?? ''),
          const SizedBox(height: 16),
          Text('Explanation', style: Theme.of(context).textTheme.titleSmall),
          Text(_reply!.answer),
          if (_reply!.sources.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 8), child: Text(_reply!.sources.join('\n'), style: Theme.of(context).textTheme.bodySmall)),
        ],
      ]),
    );
  }
}
