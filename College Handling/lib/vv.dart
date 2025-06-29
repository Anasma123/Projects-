import 'dart:convert';
import 'package:http/http.dart' as http;

import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'Signup.dart';
import 'home.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nominations',
      theme: ThemeData(

        // colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MySendNominations(title: 'Nominations'),
    );
  }
}

class MySendNominations extends StatefulWidget {
  const MySendNominations({super.key, required this.title});




  final String title;

  @override
  State<MySendNominations> createState() => _MySendNominationsState();
}

List<String> list = <String>[];


class _MySendNominationsState extends State<MySendNominations> {
  _MySendNominationsState(){
    getdata();
  }
  List<int> election_id_ = <int>[];
  List<String> election_name_ = <String>[];
  TextEditingController subdatecontroller=new TextEditingController();
  String dropdownValue1 ="";


  @override
  Widget build(BuildContext context) {

    return Scaffold(
      // backgroundColor: Colors.orange[100],

      appBar: AppBar(
        automaticallyImplyLeading: false,
        // backgroundColor: Colors.brown,
        // foregroundColor: Colors.orange[700],
        //
        // title: Text(widget.title),
      ),
      body: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
              image: AssetImage('assets/images/login.png'), fit: BoxFit.cover),

        ),

        child: Center(

          child: Container(


            child: Column(

              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                Container(
                  decoration: BoxDecoration(
                    color: Colors.grey,
                    border: Border.all(color: Colors.black12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(

                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Election:         ',
                        style: TextStyle(
                          fontSize: 15.0,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),),
                      DropdownButton<String>(
                        // isExpanded: true,
                        value: dropdownValue1,
                        onChanged: (String? value) {

                          print(dropdownValue1);
                          print("Hiiii");
                          setState(() {
                            dropdownValue1 = value!;
                          });
                        },
                        items: election_name_.map((String value) {
                          return DropdownMenuItem(

                            value: value,
                            child: Text(value,
                              style: TextStyle(
                                fontSize: 15.0,
                                fontWeight: FontWeight.bold,
                                color: Colors.black,
                                // backgroundColor: Colors.brown,
                              ),),
                          );
                        }).toList(),
                      ),

                    ],
                  ),
                ),


                SizedBox(height: 50.0),


                ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Color.fromARGB(234, 100, 68, 28),

                      foregroundColor: Colors.white,
                    ),
                    onPressed: (){_send_data();}, child: Text('send'))

              ],
            ),
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(onPressed: () {

        // Navigator.push(
        //     context,
        //     MaterialPageRoute(builder: (context) => MyHomePage(title: 'home')));

      },
        backgroundColor:Color.fromARGB(234, 100, 68, 28),
        child: Icon(Icons.home_filled),
      ),

    );
  }
  void getdata() async{
    List<int> election_id = <int>[];
    List<String> election_name = <String>[];


    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    final urls = Uri.parse('$url/View_elenamein_nomination/');


    var data = await http.post(urls, body: {});
    var jsondata = json.decode(data.body);
    String status = jsondata['status'];

    var arr = jsondata["data"];


    for (int i = 0; i < arr.length; i++) {
      election_id.add(arr[i]['id']);
      election_name.add(arr[i]['election_name']);
    }
    setState(() {
      election_id_ = election_id;
      election_name_ = election_name;
      dropdownValue1= election_name_.first;
    });
  }
  void _send_data() async{




    print(election_name_.indexOf(dropdownValue1));


    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    String lid = sh.getString('lid').toString();

    final urls = Uri.parse('$url/Send_nominations_post/');
    try {
      final response = await http.post(urls, body: {

        'lid':lid,
        'electionname' : election_id_[ election_name_.indexOf(dropdownValue1)].toString()

      });
      print(jsonDecode(response.body));
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        print(status);
        if (status=='ok') {
          // Navigator.push(context, MaterialPageRoute(
          //   builder: (context) => MyHomePage(title: "nominations"),));
        }else if (status=="exists") {
          Fluttertoast.showToast(msg: 'Already have a nomination');
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