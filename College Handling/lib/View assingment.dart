import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import 'home.dart';

void main() {
  runApp(const ViewAssingment());
}

class ViewAssingment extends StatelessWidget {
  const ViewAssingment({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const ViewAssingmentPage(title: 'View Reply'),
    );
  }
}

class ViewAssingmentPage extends StatefulWidget {
  const ViewAssingmentPage({super.key, required this.title});

  final String title;

  @override
  State<ViewAssingmentPage> createState() => _ViewAssingmentPageState();
}

class _ViewAssingmentPageState extends State<ViewAssingmentPage> {

  _ViewAssingmentPageState(){
    ViewAssingment();
  }

  List<String> id_ = <String>[];
  List<String> title_= <String>[];
  List<String> date_= <String>[];
  List<String> description_= <String>[];
  List<String> subject_= <String>[];


  Future<void> ViewAssingment() async {
    List<String> id = <String>[];
    List<String> title = <String>[];
    List<String> date = <String>[];
    List<String> description = <String>[];
    List<String> subject = <String>[];



    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewassingment/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        title.add(arr[i]['title']);
        date.add(arr[i]['date']);
        description.add(arr[i]['description']);
        subject.add(arr[i]['subject']);



      }

      setState(() {
        id_ = id;
        title_ = title;
        date_ = date;
        description_ = description;
        subject_ = subject;

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
        body:   ListView.builder(
          physics: BouncingScrollPhysics(),
          itemCount: id_.length,
          itemBuilder: (BuildContext context, int index) {
            return Padding(
              padding: const EdgeInsets.all(8.0),
              child: Card(
                elevation: 8,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                color: Colors.blueAccent,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      buildRow('Title', title_[index]),
                      buildRow('Date', date_[index]),
                      buildRow('ID', id_[index]),
                      buildRow('Subject', subject_[index]),
                      buildRow('Description', description_[index]),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),







    );
  }
  Widget buildRow(String title, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$title: ',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}



