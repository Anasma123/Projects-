import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

// import 'sendcomplaint.dart';
void main() {
  runApp(const ViewComplaintReply());
}

class ViewComplaintReply extends StatelessWidget {
  const ViewComplaintReply({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View doubt Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const student_dowtreply(title: 'View doubt Reply'),
    );
  }
}

class student_dowtreply extends StatefulWidget {
  const student_dowtreply({super.key, required this.title});

  final String title;

  @override
  State<student_dowtreply> createState() => _student_dowtreplyState();
}

class _student_dowtreplyState extends State<student_dowtreply> {

  _student_dowtreplyState(){
    ViewComplaintReply();
  }

  List<String> id_ = <String>[];
  List<String> date_= <String>[];
  List<String> SUBJECT_= <String>[];
  List<String> Doubt_= <String>[];
  List<String> Reply_= <String>[];

  Future<void> ViewComplaintReply() async {
    List<String> id = <String>[];
    List<String> date = <String>[];
    List<String> SUBJECT = <String>[];
    List<String> Doubt = <String>[];
    List<String> Reply = <String>[];


    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_dowtreply/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        id.add(arr[i]['id'].toString());
        date.add(arr[i]['date'].toString());
        SUBJECT.add(arr[i]['SUBJECT'].toString());
        Doubt.add(arr[i]['Doubt'].toString());
        Reply.add(arr[i]['Reply'].toString());
      }

      setState(() {
        id_ = id;
        date_ = date;
        SUBJECT_ = SUBJECT;
        Doubt_ = Doubt;
        Reply_ = Reply;
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

            // Navigator.push(
            //   context,
            //   MaterialPageRoute(builder: (context) => HomeNew()),);

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
                                    child: Text(date_[index]),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Text(SUBJECT_[index]),
                                  ),    Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Text(Doubt_[index]),
                                  ),  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Text(Reply_[index]),

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
        floatingActionButton: FloatingActionButton(onPressed: () {

          // Navigator.push(
          //     context,
          //     MaterialPageRoute(builder: (context) => MySendComplaint()));

        },
          child: Icon(Icons.add),
        ),


      ),
    );
  }
}

