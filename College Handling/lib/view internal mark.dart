import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

import 'home.dart';

void main() {
  runApp(const ViewInternalMark());
}

class ViewInternalMark extends StatelessWidget {
  const ViewInternalMark({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const ViewInternalMarkPage(title: 'View Reply'),
    );
  }
}

class ViewInternalMarkPage extends StatefulWidget {
  const ViewInternalMarkPage({super.key, required this.title});

  final String title;

  @override
  State<ViewInternalMarkPage> createState() => _ViewInternalMarkPageState();
}

class _ViewInternalMarkPageState extends State<ViewInternalMarkPage> {

  _ViewInternalMarkPageState(){
    ViewInternalMark();
  }

  List<String> id_ = <String>[];
  List<String> internal_mark_= <String>[];
  List<String> subject_= <String>[];
  List<String> date_= <String>[];


  Future<void> ViewInternalMark() async {
    List<String> id = <String>[];
    List<String> internal_mark = <String>[];
    List<String> subject = <String>[];
    List<String> date = <String>[];



    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewinternalmark/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        internal_mark.add(arr[i]['internalmark'].toString());
        subject.add(arr[i]['subject'].toString());
        date.add(arr[i]['date'].toString());



      }

      setState(() {
        id_ = id;
        internal_mark_ = internal_mark;
        subject_ = subject;
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
                                        Text('internal mark'),
                                        Text(internal_mark_[index]),
                                      ],
                                    ),
                                  ),
                                  Padding(
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
                                        Text('subject'),
                                        Text(subject_[index]),
                                      ],
                                    ),

                                  )
                                  ,
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


