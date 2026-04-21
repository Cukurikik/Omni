// ==========================================
// 🔐 OMNI FIREBASE AUTHENTICATION (SDK)
// ==========================================
// Integrasi Otorisasi Multi-Level Native OMNI Mobile SDK
//
// NOTE: In a Flutter project with firebase_auth installed,
// replace the stubs below with:
//   import 'package:firebase_auth/firebase_auth.dart';

import 'dart:async';

// ---- Standalone Stubs (for analysis without Firebase SDK) ----

class User {
  final String uid;
  final String? email;
  final bool isAnonymous;
  User({required this.uid, this.email, this.isAnonymous = false});

  Future<String?> getIdToken() async => 'omni-jwt-token-$uid';
}

class UserCredential {
  final User? user;
  UserCredential({this.user});
}

class FirebaseAuth {
  static final FirebaseAuth _instance = FirebaseAuth._();
  FirebaseAuth._();
  static FirebaseAuth get instance => _instance;

  User? _currentUser;
  User? get currentUser => _currentUser;

  final StreamController<User?> _authStateController =
      StreamController<User?>.broadcast();

  Stream<User?> authStateChanges() => _authStateController.stream;

  Future<UserCredential> signInAnonymously() async {
    _currentUser = User(uid: 'anon-${DateTime.now().millisecondsSinceEpoch}', isAnonymous: true);
    _authStateController.add(_currentUser);
    return UserCredential(user: _currentUser);
  }

  Future<UserCredential> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    _currentUser = User(uid: 'user-${email.hashCode}', email: email);
    _authStateController.add(_currentUser);
    return UserCredential(user: _currentUser);
  }

  Future<void> signOut() async {
    _currentUser = null;
    _authStateController.add(null);
  }
}

// ---- OMNI Auth Manager ----

class OmniAuthManager {
  final FirebaseAuth _auth = FirebaseAuth.instance;

  /// Stream listening untuk mendeteksi status pengguna OMNI aktif
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  /// Sign In Anonymous (Trial Mode)
  Future<UserCredential?> signInAnonymously() async {
    try {
      print("🕵️‍♂️ [OMNI-AUTH] Melakukan Authentikasi Anonim (Trial Mode)...");
      return await _auth.signInAnonymously();
    } catch (e) {
      print("❌ [OMNI-AUTH] Kegagalan Anonim: $e");
      return null;
    }
  }

  /// Sign In Provider Resmi (Enterprise)
  Future<UserCredential?> signInWithEmail(String email, String password) async {
    try {
      print("🏢 [OMNI-AUTH] Melakukan Authentikasi Enterprise ($email)...");
      return await _auth.signInWithEmailAndPassword(
          email: email, password: password);
    } catch (e) {
      print("❌ [OMNI-AUTH] Kredensial Enterprise Ditolak: $e");
      return null;
    }
  }

  /// Mengambil Token Akses RAG & Data Connect
  Future<String?> getOmniAccessToken() async {
    final user = _auth.currentUser;
    if (user != null) {
      return await user.getIdToken();
    }
    return null;
  }

  Future<void> signOut() async {
    print("👋 [OMNI-AUTH] Sesi agen eksekutif dihentikan.");
    await _auth.signOut();
  }

  Map<String, dynamic> getDiagnostics() => {
    'currentUser': _auth.currentUser?.uid,
    'isAuthenticated': _auth.currentUser != null,
    'isAnonymous': _auth.currentUser?.isAnonymous ?? false,
  };
}
