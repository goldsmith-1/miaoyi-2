import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiException implements Exception {
  ApiException(this.message);
  final String message;
  @override
  String toString() => message;
}

class Reply {
  const Reply({required this.answer, required this.sources, this.extractedText});
  final String answer;
  final List<String> sources;
  final String? extractedText;
}

/// Talks to the FastAPI backend. The token provider returns the Supabase access token for the signed-in user.
class ApiClient {
  ApiClient({http.Client? client, Future<String?> Function()? token})
      : _http = client ?? http.Client(),
        _token = token ?? (() async => const String.fromEnvironment('DEV_TOKEN'));

  static const baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000');
  final http.Client _http;
  final Future<String?> Function() _token;

  Future<Map<String, String>> _auth() async {
    final t = await _token();
    return {if (t != null && t.isNotEmpty) 'authorization': 'Bearer $t'};
  }

  Reply _parse(http.Response r) {
    if (r.statusCode == 429) throw ApiException('Too many requests. Please wait a minute.');
    if (r.statusCode == 401) throw ApiException('Please sign in again.');
    if (r.statusCode != 200) {
      String detail = 'Something went wrong (${r.statusCode}).';
      try {
        detail = (jsonDecode(r.body)['detail'] ?? detail).toString();
      } catch (_) {}
      throw ApiException(detail);
    }
    final j = jsonDecode(utf8.decode(r.bodyBytes)) as Map<String, dynamic>;
    return Reply(
      answer: j['answer'] as String,
      sources: [for (final s in (j['sources'] as List? ?? [])) '[${s['n']}] ${s['title']}'],
      extractedText: j['extracted_text'] as String?,
    );
  }

  Future<Reply> chat(String message, List<Map<String, String>> history) async {
    try {
      final r = await _http
          .post(Uri.parse('$baseUrl/v1/chat'),
              headers: {'content-type': 'application/json', ...await _auth()},
              body: jsonEncode({'message': message, 'history': history}))
          .timeout(const Duration(seconds: 60));
      return _parse(r);
    } on ApiException {
      rethrow;
    } catch (_) {
      throw ApiException('Could not reach the server. Check your connection.');
    }
  }

  Future<Reply> scan(Uint8List bytes, String filename, String mime) async {
    try {
      final req = http.MultipartRequest('POST', Uri.parse('$baseUrl/v1/scan'))
        ..headers.addAll(await _auth())
        ..files.add(http.MultipartFile.fromBytes('image', bytes, filename: filename, contentType: MediaType.parse(mime)));
      final r = await http.Response.fromStream(await _http.send(req).timeout(const Duration(seconds: 90)));
      return _parse(r);
    } on ApiException {
      rethrow;
    } catch (_) {
      throw ApiException('Could not reach the server. Check your connection.');
    }
  }
}
