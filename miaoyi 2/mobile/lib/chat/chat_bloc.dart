import 'package:flutter_bloc/flutter_bloc.dart';

import '../api/api_client.dart';

class Msg {
  const Msg({required this.fromUser, required this.text, this.sources = const []});
  final bool fromUser;
  final String text;
  final List<String> sources;
}

sealed class ChatEvent {}

class Sent extends ChatEvent {
  Sent(this.text);
  final String text;
}

class ChatState {
  const ChatState({this.messages = const [], this.loading = false, this.error});
  final List<Msg> messages;
  final bool loading;
  final String? error;
}

class ChatBloc extends Bloc<ChatEvent, ChatState> {
  ChatBloc(this._api) : super(const ChatState()) {
    on<Sent>(_onSent);
  }
  final ApiClient _api;

  Future<void> _onSent(Sent e, Emitter<ChatState> emit) async {
    final history = [
      for (final m in state.messages.reversed.take(6).toList().reversed)
        {'role': m.fromUser ? 'user' : 'assistant', 'content': m.text}
    ];
    emit(ChatState(messages: [...state.messages, Msg(fromUser: true, text: e.text)], loading: true));
    try {
      final r = await _api.chat(e.text, history);
      emit(ChatState(messages: [...state.messages, Msg(fromUser: false, text: r.answer, sources: r.sources)]));
    } on ApiException catch (err) {
      emit(ChatState(messages: state.messages, error: err.message));
    }
  }
}
