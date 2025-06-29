import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import 'login.dart';
void main() {
  runApp(const MyChangePassword());
}

class MyChangePassword extends StatelessWidget {
  const MyChangePassword({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ChangePassword',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyChangePasswordPage(title: 'ChangePassword'),
    );
  }
}

class MyChangePasswordPage extends StatefulWidget {
  const MyChangePasswordPage({super.key, required this.title});

  final String title;

  @override
  State<MyChangePasswordPage> createState() => _MyChangePasswordPageState();
}

class _MyChangePasswordPageState extends State<MyChangePasswordPage> {


  @override
  Widget build(BuildContext context) {

    TextEditingController oldpasswordController= new TextEditingController();
    TextEditingController newpasswordController= new TextEditingController();
    TextEditingController comfirmpasswordController= new TextEditingController();




    return WillPopScope(
      onWillPop: () async{ return true; },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.primary,
          title: Text(widget.title),
        ),
        body: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[

              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: oldpasswordController,


                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("Old Password")),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: newpasswordController,

                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("New Password")),
                ),
              ),      Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: comfirmpasswordController,

                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("Confirm Password")),
                ),
              ),

              ElevatedButton(
                onPressed: () async {

                  String oldp= oldpasswordController.text.toString();
                  String old= newpasswordController.text.toString();
                  String ol= comfirmpasswordController.text.toString();





                  SharedPreferences sh = await SharedPreferences.getInstance();
                  String url = sh.getString('url').toString();
                  String lid = sh.getString('lid').toString();

                  final urls = Uri.parse('$url/student_changepassword/');
                  try {
                    final response = await http.post(urls, body: {
                      'oldpassword':oldp,
                      'newpasswoard':old,
                      'comfirmpasswoard':ol,
                      'lid':lid



                    });
                    if (response.statusCode == 200) {
                      String status = jsonDecode(response.body)['status'];
                      if (status=='ok') {
                        Fluttertoast.showToast(msg: 'Password Changed Successfully');
                        // Navigator.push(
                        //     context,
                        //     MaterialPageRoute(builder: (context) => MyLoginPage(title: 'Login',)));
                      }else {
                        Fluttertoast.showToast(msg: 'Incorrect Password');
                      }
                    }
                    else {
                      Fluttertoast.showToast(msg: 'Network Error');
                    }
                  }
                  catch (e){
                    Fluttertoast.showToast(msg: e.toString());
                  }

                },
                child: Text("ChangePassword"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
