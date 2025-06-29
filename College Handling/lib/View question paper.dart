import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

import 'home.dart';
final Uri _url = Uri.parse('https://flutter.dev');

void main() {
  runApp(const ViewQuestionPaper());
}

class ViewQuestionPaper extends StatelessWidget {
  const ViewQuestionPaper({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const ViewQuestionPaperPage(title: 'View Reply'),
    );
  }
}

class ViewQuestionPaperPage extends StatefulWidget {
  const ViewQuestionPaperPage({super.key, required this.title});

  final String title;

  @override
  State<ViewQuestionPaperPage> createState() => _ViewQuestionPaperPageState();
}

class _ViewQuestionPaperPageState extends State<ViewQuestionPaperPage> {

  _ViewQuestionPaperPageState(){
    ViewQuestionPaper();
  }

  List<String> id_ = <String>[];
  List<String> upload_file_= <String>[];
  List<String> subject_name_= <String>[];
  List<String> date_= <String>[];


  Future<void> ViewQuestionPaper() async {
    List<String> id = <String>[];
    List<String> upload_file = <String>[];
    List<String> subject_name = <String>[];
    List<String> date = <String>[];



    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewqutionpaper/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        upload_file.add(sh.getString('imageurl').toString()+arr[i]['upload file'].toString());
        subject_name.add(arr[i]['subject name'].toString());
        date.add(arr[i]['date'].toString());



      }

      setState(() {
        id_ = id;
        upload_file_ = upload_file;
        subject_name_ = subject_name;
        date_ = date;

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
                                        ElevatedButton(
                                          onPressed: () async {
                                            String fileUrl = upload_file_[index];
                                            if (!await launchUrl(Uri.parse(upload_file_[index]))) {
                                              throw Exception('could not load');
                                              // await launch(fileUrl);
                                            } else {
                                              throw 'Could not launch $fileUrl';
                                            }
                                          },
                                          child: Text("Download"),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Row(
                                      children: [
                                        Text('subject'),
                                        Text(subject_name_[index]),
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


