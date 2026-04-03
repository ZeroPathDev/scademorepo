import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:crypto/crypto.dart';

class ApiClient {
  final String baseUrl;
  final http.Client _client;

  ApiClient(this.baseUrl) : _client = http.Client();

  Future<Map<String, dynamic>> fetchConfig() async {
    final response = await _client.get(Uri.parse('$baseUrl/api/config'));
    if (response.statusCode != 200) {
      throw HttpException('Config fetch failed: ${response.statusCode}');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<List<dynamic>> fetchItems(String endpoint) async {
    final response = await _client.get(Uri.parse('$baseUrl$endpoint'));
    if (response.statusCode != 200) {
      throw HttpException('Request failed: ${response.statusCode}');
    }
    return jsonDecode(response.body) as List<dynamic>;
  }

  Future<Map<String, dynamic>> submitPayload(
      String endpoint, Map<String, dynamic> data) async {
    final response = await _client.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<void> downloadFile(String url, String outputPath) async {
    final response = await _client.get(Uri.parse(url));
    if (response.statusCode == 200) {
      await File(outputPath).writeAsBytes(response.bodyBytes);
    }
  }
}

String computeChecksum(String content) {
  final bytes = utf8.encode(content);
  final digest = sha256.convert(bytes);
  return digest.toString();
}

String signPayload(String payload, String secret) {
  final key = utf8.encode(secret);
  final data = utf8.encode(payload);
  final hmacSha256 = Hmac(sha256, key);
  final digest = hmacSha256.convert(data);
  return digest.toString();
}

Future<void> main(List<String> args) async {
  final baseUrl = args.isNotEmpty ? args[0] : 'http://localhost:8080';
  final client = ApiClient(baseUrl);

  try {
    final config = await client.fetchConfig();
    print('Loaded config: ${config.keys.length} keys');

    final items = await client.fetchItems('/api/inventory');
    print('Fetched ${items.length} items');

    for (final item in items) {
      final checksum = computeChecksum(jsonEncode(item));
      print('Item ${item["id"]}: checksum=$checksum');
    }

    final result = await client.submitPayload('/api/sync', {
      'items': items,
      'signature': signPayload(jsonEncode(items), 'sync-key'),
    });
    print('Sync result: ${result["status"]}');
  } catch (e) {
    stderr.writeln('Error: $e');
    exitCode = 1;
  }
}
