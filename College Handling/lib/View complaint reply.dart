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
      title: 'View complaint Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const ViewComplaintReplyPage(title: 'View complaint Reply'),
    );
  }
}

class ViewComplaintReplyPage extends StatefulWidget {
  const ViewComplaintReplyPage({super.key, required this.title});

  final String title;

  @override
  State<ViewComplaintReplyPage> createState() => _ViewComplaintReplyPageState();
}

class _ViewComplaintReplyPageState extends State<ViewComplaintReplyPage> {

  _ViewComplaintReplyPageState(){
    ViewComplaintReply();
  }

  List<String> id_ = <String>[];
  List<String> date_= <String>[];
  List<String> complaint_= <String>[];
  List<String> reply_= <String>[];
  List<String> status_= <String>[];

  Future<void> ViewComplaintReply() async {
    List<String> id = <String>[];
    List<String> date = <String>[];
    List<String> complaint = <String>[];
    List<String> reply = <String>[];
    List<String> status = <String>[];


    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewcompliatreply/';

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
        complaint.add(arr[i]['complaint'].toString());
        reply.add(arr[i]['reply'].toString());
        status.add(arr[i]['status'].toString());
      }

      setState(() {
        id_ = id;
        date_ = date;
        complaint_ = complaint;
        reply_ = reply;
        status_ = status;
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
                                    child: Text(complaint_[index]),
                                  ),    Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Text(reply_[index]),
                                  ),  Padding(
                                    padding: EdgeInsets.all(5),
                                    child: Text(status_[index]),
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

