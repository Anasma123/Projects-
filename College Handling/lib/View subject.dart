import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/chat.dart';

import 'Doubt clearance.dart';
import 'home.dart';

void main() {
  runApp(const ViewSubject());
}

class ViewSubject extends StatelessWidget {
  const ViewSubject({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const ViewSubjectPage(title: 'View Reply'),
    );
  }
}

class ViewSubjectPage extends StatefulWidget {
  const ViewSubjectPage({super.key, required this.title});

  final String title;

  @override
  State<ViewSubjectPage> createState() => _ViewSubjectPageState();
}

class _ViewSubjectPageState extends State<ViewSubjectPage> {

  _ViewSubjectPageState(){
    ViewSubject();
  }

  List<String> id_ = <String>[];
  List<String> staff_= <String>[];
  List<String> course_= <String>[];
  List<String> subject_= <String>[];
  List<String> staff_lid_= <String>[];


  Future<void> ViewSubject() async {
    List<String> id = <String>[];
    List<String> staff = <String>[];
    List<String> course = <String>[];
    List<String> subject = <String>[];
    List<String> staff_lid = <String>[];



    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewsubject/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        staff.add(arr[i]['name'].toString());
        course.add(arr[i]['course'].toString());
        subject.add(arr[i]['subject'].toString());
        staff_lid.add(arr[i]['staff_lid'].toString());



      }

      setState(() {
        id_ = id;
        staff_ = staff;
        course_ = course;
        subject_ = subject;
        staff_lid_ = staff_lid;

      });

      print(statuss);
    } catch (e) {
      print("Error ------------------- " + e.toString());
      //there is error during converting file image to base64 encoding.
    }
  }




  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView.builder(
        physics: BouncingScrollPhysics(),
        itemCount: id_.length,
        itemBuilder: (BuildContext context, int index) {
          return buildListTile(context, index);
        },
      ),
    );
  }
  Widget buildListTile(BuildContext context, int index) {
    return Card(
      elevation: 8,
      margin: EdgeInsets.all(10),
      color: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            buildText('Staff:', staff_[index], Colors.green),
            buildText('Course:', course_[index], Colors.orange),
            buildText('Subject:', subject_[index], Colors.purple),
            buildText('ID:', id_[index], Colors.red),
            SizedBox(height: 10),
            buildButtonRow(context, index),
          ],
        ),
      ),
    );
  }

  Widget buildText(String title, String value, Color color) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 5),
      child: RichText(
        text: TextSpan(
          style: TextStyle(
            color: Colors.black,
            fontSize: 16,
            fontWeight: FontWeight.bold,
            fontFamily: 'Roboto', // Example custom font
          ),
          children: [
            TextSpan(text: '$title '),
            TextSpan(
              text: value,
              style: TextStyle(
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildButtonRow(BuildContext context, int index) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        ElevatedButton(
          onPressed: () async {
            SharedPreferences sh = await SharedPreferences.getInstance();
            sh.setString('aid', staff_lid_[index]);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => StudentChatPage(title: 'Chat')),
            );
          },
          child: Text(
            'Chat',
            style: TextStyle(
              fontFamily: 'Roboto', // Example custom font
            ),
          ),
          style: ElevatedButton.styleFrom(
            primary: Colors.blue,
            padding: EdgeInsets.symmetric(horizontal: 20),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ),
        ElevatedButton(
          onPressed: () async {
            SharedPreferences sh = await SharedPreferences.getInstance();
            sh.setString('aid', id_[index]);
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => DowbtClearness()),
            );
          },
          child: Text(
            'Doubt',
            style: TextStyle(
              fontFamily: 'Roboto', // Example custom font
            ),
          ),
          style: ElevatedButton.styleFrom(
            primary: Colors.red,
            padding: EdgeInsets.symmetric(horizontal: 20),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ),
      ],
    );
  }
}


