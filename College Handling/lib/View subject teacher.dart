import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import 'home.dart';

void main() {
  runApp(const ViewSubjectTeacher());
}

class ViewSubjectTeacher extends StatelessWidget {
  const ViewSubjectTeacher({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const ViewSubjectTeacherPage(title: 'View Reply'),
    );
  }
}

class ViewSubjectTeacherPage extends StatefulWidget {
  const ViewSubjectTeacherPage({super.key, required this.title});

  final String title;

  @override
  State<ViewSubjectTeacherPage> createState() => _ViewSubjectTeacherPageState();
}

class _ViewSubjectTeacherPageState extends State<ViewSubjectTeacherPage> {

  _ViewSubjectTeacherPageState(){
    ViewSubjectTeacher();
  }

  List<String> id_ = <String>[];
  List<String> name_= <String>[];
  List<String> phone_number_= <String>[];
  List<String> mail_= <String>[];
  List<String> photo_= <String>[];
  List<String> department_= <String>[];
  List<String> dob_= <String>[];


  Future<void> ViewSubjectTeacher() async {
    List<String> id = <String>[];
    List<String> name = <String>[];
    List<String> phone_number = <String>[];
    List<String> mail = <String>[];
    List<String> photo = <String>[];
    List<String> department = <String>[];
    List<String> dob = <String>[];



    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/myapp/student_ViewSubjectTeacher/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        name.add(arr[i]['name']);
        phone_number.add(arr[i]['phone_number']);
        mail.add(arr[i]['mail']);
        photo.add(arr[i]['photo']);
        department.add(arr[i]['department']);
        dob.add(arr[i]['dob']);


      }

      setState(() {
        id_ = id;
        name_ = name;
        phone_number_ = phone_number;
        mail_ = mail;
        photo_ = photo;
        department_ = department;
        dob_ = dob;

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
              MaterialPageRoute(builder: (context) => MyhomePage(title: '',)),);

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
                                        Text('Name'),
                                        Text(name_[index]),
                                      ],
                                    ),
                                  ),Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('dob'),
                                        Text(dob_[index]),
                                      ],
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('phone_number'),
                                        Text(phone_number_[index]),
                                      ],
                                    ),
                                  ),Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('mail'),
                                        Text(mail_[index]),
                                      ],
                                    ),
                                  ),Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('photo'),
                                        Text(photo_[index]),
                                      ],
                                    ),
                                  ),Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('department'),
                                        Text(department_[index]),
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
