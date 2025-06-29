import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:http/http.dart' as http;

import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/Signup.dart';
import 'package:studybuddy/constants/colors.dart';
import 'package:studybuddy/pages/home/home_screen.dart';
import 'package:studybuddy/utils/routes/routes.dart';

import '../../View study materials.dart';
import '../../forgot.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  late TextEditingController _unameController;
  late TextEditingController _passwordController;
  bool isObscure = true;

  @override
  void initState() {
    super.initState();

    _unameController = TextEditingController();
    _passwordController = TextEditingController();
  }

  @override
  void dispose() {
    _unameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: GestureDetector(
        onTap: () {
          FocusScope.of(context).unfocus();
        },
        child: Stack(
          children: [
            Positioned.fill(
              child: Image.asset(
                'assets/images/f.png',
                fit: BoxFit.cover,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "WELCOME",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.pink, fontSize: 40, fontWeight: FontWeight.w900),
                  ),
                  SizedBox(height: 10),
                  Text(
                    "STUDY BUDDY !",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.white, fontSize: 35, fontWeight: FontWeight.w700),
                  ),
                  SizedBox(height: 10),
                  Text(
                    "(To Studybuddy \nAn Educational Platform )",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.yellow, fontSize: 15, fontWeight: FontWeight.w400, fontStyle: FontStyle.italic),
                  ),
                  SizedBox(height: 30),
                  TextField(
                    controller: _unameController,
                    obscureText: false,
                    style: TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Email',
                      hintStyle: TextStyle(color: Colors.white.withOpacity(0.7)),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8.0)),
                      filled: true,
                      fillColor: Colors.black.withOpacity(0.5),
                      prefixIcon: Icon(Icons.email, color: Colors.white),
                    ),
                  ),
                  SizedBox(height: 10),
                  TextField(
                    controller: _passwordController,
                    obscureText: isObscure,
                    style: TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Password',
                      hintStyle: TextStyle(color: Colors.white.withOpacity(0.7)),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8.0)),
                      filled: true,
                      fillColor: Colors.black.withOpacity(0.5),
                      prefixIcon: Icon(Icons.lock, color: Colors.white),
                      suffixIcon: IconButton(
                        onPressed: () {
                          setState(() {
                            isObscure = !isObscure;
                          });
                        },
                        icon: SvgPicture.asset(
                          'assets/icon/password_suffix_icon.svg',
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(height: 20),
                  InkWell(
                    onTap: () {
                      Navigator.push(context, MaterialPageRoute(builder: (context) => ForgotPasswordForm()));
                    },
                    child: Align(
                      alignment: Alignment.centerRight,
                      child: Text(
                        "Forgot your password?",
                        style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                  SizedBox(height: 10),
                  InkWell(
                    onTap: () {
                      Navigator.push(context, MaterialPageRoute(builder: (context) => MyMySignupPage(title: '')));
                    },
                    child: Align(
                      alignment: Alignment.centerRight,
                      child: Text(
                        "Don't have an account? Sign up",
                        style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                  SizedBox(height: 30),
                  ElevatedButton(
                    onPressed: () {
                      _sendData();
                    },
                    style: ElevatedButton.styleFrom(
                      primary: AppColors.mainGreen,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
                      padding: EdgeInsets.symmetric(vertical: 15),
                    ),
                    child: Text(
                      'Login',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  void _sendData() async {
    String uname = _unameController.text;
    String ps = _passwordController.text;

    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();

    final urls = Uri.parse('$url/student_login/');
    try {
      final response = await http.post(urls, body: {
        'name': uname,
        'password': ps,
      });
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        if (status == 'ok') {
          String lid = jsonDecode(response.body)['lid'];
          sh.setString("lid", lid);

          Navigator.push(context, MaterialPageRoute(builder: (context) => HomeScreen()));
        } else {
          Fluttertoast.showToast(msg: 'Not Found');
        }
      } else {
        Fluttertoast.showToast(msg: 'Network Error');
      }
    } catch (e) {
      Fluttertoast.showToast(msg: e.toString());
    }
  }
}