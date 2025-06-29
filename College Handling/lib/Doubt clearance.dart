import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/pages/home/home_screen.dart';
import 'package:studybuddy/signup.dart';

import 'home.dart';


void main() {
  runApp(const DowbtClearness());
}

class DowbtClearness extends StatelessWidget {
  const DowbtClearness({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Login',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const DowbtClearnessPage(title: 'Login'),
    );
  }
}

class DowbtClearnessPage extends StatefulWidget {
  const DowbtClearnessPage({super.key, required this.title});

  final String title;

  @override
  State<DowbtClearnessPage> createState() => _DowbtClearnessPageState();
}

class _DowbtClearnessPageState extends State<DowbtClearnessPage> {


  TextEditingController dowbtController = new TextEditingController();


  @override
  Widget build(BuildContext context) {

    return WillPopScope(
      onWillPop: () async{ return true; },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: Text(widget.title),
        ),


        body: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[

              Padding(
                padding: const EdgeInsets.all(8),
                child: TextField(
                  controller: dowbtController,
                  decoration: InputDecoration(border: OutlineInputBorder(),label: Text("doubt")),
                ),
              ),


              ElevatedButton(
                onPressed: () {
                  _send_data();





                },
                child: Text("send"),
              ),
            ],
          ),
        ),
      ),
    );
  }



  void _send_data() async{


    String dowbt=dowbtController.text;



    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    String aid = sh.getString('aid').toString();
    String lid = sh.getString('lid').toString();

    final urls = Uri.parse('$url/studentsenddout/');
    try {
      final response = await http.post(urls, body: {

        'dowbt':dowbt,
        'aid':aid,
        'lid':lid,


      });
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        if (status=='ok') {




          Navigator.push(context, MaterialPageRoute(
            builder: (context) => HomeScreen(),));
        }else {
          Fluttertoast.showToast(msg: 'Not Found');
        }
      }
      else {
        Fluttertoast.showToast(msg: 'Network Error');
      }
    }
    catch (e){
      Fluttertoast.showToast(msg: e.toString());
    }
  }


}

