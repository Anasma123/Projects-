import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/pages/home/home_screen.dart';

import 'home.dart';

void main() {
  runApp(const ViewAttendence());
}

class ViewAttendence extends StatelessWidget {
  const ViewAttendence({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const ViewAttendencePage(title: 'View Reply'),
    );
  }
}

class ViewAttendencePage extends StatefulWidget {
  const ViewAttendencePage({super.key, required this.title});

  final String title;

  @override
  State<ViewAttendencePage> createState() => _ViewAttendencePageState();
}

class _ViewAttendencePageState extends State<ViewAttendencePage> {

  _ViewAttendencePageState(){
    ViewAttendence();
  }

  List<String> id_ = <String>[];
  List<String> student_name_= <String>[];
  List<String> course_= <String>[];
  List<String> date_= <String>[];
  List<String> total_attendence_= <String>[];


  Future<void> ViewAttendence() async {
    List<String> id = <String>[];
    List<String> student_name = <String>[];
    List<String> course = <String>[];
    List<String> date = <String>[];
    List<String> total_attendence = <String>[];



    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewattendence/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        student_name.add(arr[i]['student name']);
        course.add(arr[i]['subject name']);
        date.add(arr[i]['date']);
        total_attendence.add(arr[i]['attendence']);



      }

      setState(() {
        id_ = id;
        student_name_ = student_name;
        course_ = course;
        date_ = date;
        total_attendence_ = total_attendence;

      });

      print(statuss);
    } catch (e) {
      print("Error ------------------- " + e.toString());
      //there is error during converting file image to base64 encoding.
    }
  }




  @override
  Widget build(BuildContext context) {



    return WillPopScope(
      onWillPop: () async{ return true; },
      child: Scaffold(
        appBar: AppBar(
          leading: BackButton( onPressed:() {

            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => HomeScreen()),);


          },),
          backgroundColor: Theme.of(context).colorScheme.primary,
          title: Text(widget.title),
        ),
        body: ListView.builder(
          physics: BouncingScrollPhysics(),
          // padding: EdgeInsets.all(5.0),
          // shrinkWrap: true,
          itemCount: id_.length,
          itemBuilder: (BuildContext context, int index) {
            return ListTile(
              onLongPress: () {
                print("long press" + index.toString());
              },
              title: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    children: [
                      Card(
                        child:
                        Row(
                            children: [
                              Column(
                                children: [
                                  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('student name'),
                                        Text(student_name_[index]),
                                      ],
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('cousre'),
                                        Text(course_[index]),
                                      ],
                                    ),
                                  ),Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('date'),
                                        Text(date_[index]),
                                      ],
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('id'),
                                        Text(id_[index]),
                                      ],
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('total attendence'),
                                        Text(total_attendence_[index]),
                                      ],
                                    ),
                                  ),
                                ],
                              ),

                            ]
                        ),

                        elevation: 8,
                        margin: EdgeInsets.all(10),
                      ),
                    ],
                  )),
            );
          },
        ),



      ),
    );
  }
}




