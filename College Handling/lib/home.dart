import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/view%20internal%20mark.dart';
import 'package:studybuddy/view%20profile.dart';
import 'View announcment.dart';
import 'Change passwoard.dart';
import 'Doubt clearance.dart';
import 'Send complaint.dart';
import 'View assingment status.dart';
import 'View assingment.dart';
import 'View attendence.dart';
import 'View complaint reply.dart';
import 'View question paper.dart';
import 'View study materials.dart';
import 'View subject teacher.dart';
import 'View subject.dart';
import 'View tutor.dart';
import 'editprofile.dart';

void main() {
  runApp(const Myhome());
}

class Myhome extends StatelessWidget {
  const Myhome({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Reply',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 18, 82, 98)),
        useMaterial3: true,
      ),
      home: const MyhomePage(title: 'View Reply'),
    );
  }
}

class MyhomePage extends StatefulWidget {
  const MyhomePage({super.key, required this.title});

  final String title;

  @override
  State<MyhomePage> createState() => _MyhomePageState();
}

class _MyhomePageState extends State<MyhomePage> {

  _MyhomePageState(){
    Myhome();
    _send_data();
  }
  List<String> title_= <String>[];
  List<String> date_= <String>[];
  List<String> announcment_= <String>[];


  Future<void> Myhome() async {
    List<String> title = <String>[];
    List<String> date = <String>[];
    List<String> announcment = <String>[];



    try {
      SharedPreferences sh = await SharedPreferences.getInstance();
      String urls = sh.getString('url').toString();
      String lid = sh.getString('lid').toString();
      String url = '$urls/student_viewtutor/';

      var data = await http.post(Uri.parse(url), body: {

        'lid':lid

      });
      var jsondata = json.decode(data.body);
      String statuss = jsondata['status'];

      var arr = jsondata["data"];

      print(arr.length);

      for (int i = 0; i < arr.length; i++) {
        title_.add(arr[i]['title']);
        date_.add(arr[i]['date']);
        announcment_.add(arr[i]['description']);



      }

      setState(() {
        title_ = title;
        date_ = date;
        announcment_ = announcment;

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
        body:
        Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Container(
                height: 200,
                decoration: BoxDecoration(
                  color: Colors.grey,
                  borderRadius: BorderRadius.circular(20)
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                  CircleAvatar(
                    backgroundImage: NetworkImage(photo_),
                    radius: 60,
                  ),
                  Padding(
                    padding: const EdgeInsets.only(right: 70,top: 50),
                    child: Container(
                      width: 150,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [

                          Text(name_,style: TextStyle(fontWeight:FontWeight.bold),),
                          Text(phone_,style: TextStyle(fontWeight:FontWeight.bold),),
                          Text(email_,style: TextStyle(fontWeight:FontWeight.bold),),
                          Text(department_,style: TextStyle(fontWeight:FontWeight.bold),),
                          Text(place_,style: TextStyle(fontWeight:FontWeight.bold),),
                        ],
                      ),
                    ),
                  ),

                ],),
              ),
            ),
            Expanded(

              child: GridView(
                  gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                    maxCrossAxisExtent: 210,
                    childAspectRatio: 10/10,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,

                  ),
                  padding: const EdgeInsets.all(8.0),
                children: [
                  Container(
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                      color: Color.fromARGB(255, 18, 82, 98),
                      borderRadius: BorderRadius.circular(15)),
                  child:  Column(
                      children: [
                        SizedBox(height: 5.0),
                        InkWell(
                          onTap: () async {
                            // final pref =await SharedPreferences.getInstance();
                            // pref.setString("did", id_[index]);
                            // Navigator.push(
                            //   context,
                            //   MaterialPageRoute(builder: (context) => ViewSchedule()),);
                          },
                          child: CircleAvatar(
                              radius: 50,backgroundImage: NetworkImage("")),
                        ),
                        // SizedBox(height: 5.0),
                        // CircleAvatar(radius: 50,backgroundImage: NetworkImage(photo_[index])),
                        Column(
                          children: [
                            Padding(
                              padding: EdgeInsets.all(1),
                              child: Text("",style: TextStyle(color: Colors.white,fontSize: 18)),
                            ),],
                        ),
                        Column(
                          children: [
                            Padding(
                              padding: EdgeInsets.all(2),
                              child: Text("",style: TextStyle(color: Colors.white)),
                            ),],
                        ),
                        Column(
                          children: [
                            Padding(
                              padding: EdgeInsets.all(1),
                              child: Text("",style: TextStyle(color: Colors.white)),
                            ),
                          ],
                        ),


                      ]
                  )
              )
                ],


                  ),
            ),
          ],
        ),




        drawer: Drawer(
          child: ListView(
            padding: const EdgeInsets.all(0),
            children: [
              const DrawerHeader(
                decoration: BoxDecoration(
                  color: Colors.green,
                ), //BoxDecoration
                child: UserAccountsDrawerHeader(
                  decoration: BoxDecoration(color: Colors.green),
                  accountName: Text(
                    "iqbal",
                    style: TextStyle(fontSize: 18),
                  ),
                  accountEmail: Text("iqbal77@gmail.com"),
                  currentAccountPictureSize: Size.square(50),
                  currentAccountPicture: CircleAvatar(
                    backgroundColor: Color.fromARGB(255, 165, 255, 137),
                    child: Text(
                      "A",
                      style: TextStyle(fontSize: 30.0, color: Colors.blue),
                    ), //Text
                  ), //circleAvatar
                ), //UserAccountDrawerHeader
              ), //DrawerHeader
              ListTile(
                leading: const Icon(Icons.person),
                title: const Text(' My Profile '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewProfilePage(title: '',)),);
                },
              ),
              ListTile(
                leading: const Icon(Icons.book),
                title: const Text(' Change my Password '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => MyChangePassword()),);

                },
              ),
              ListTile(
                leading: const Icon(Icons.workspace_premium),
                title: const Text(' Chat With Teachers '),
                onTap: () {
                  Navigator.pop(context);
                  // Navigator.push(
                  //   context,
                  //   MaterialPageRoute(builder: (context) => ()),);
                },
              ),
              ListTile(
                leading: const Icon(Icons.video_label),
                title: const Text(' Doubt Clearans '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => DowbtClearness()),);
                },
              ),
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' Edit Profile '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => EditProfile()),);
                },
              ),
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' Send Complaint'),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => SendComplaint()),);
                },
              ),ListTile(
                leading:  Icon(Icons.edit),
                title:  Text(' View Announcment '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewAnnouncementPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Assingment '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewAssingment()),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Assingment Status '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewAssingmentStatus()),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' view subject Attendence '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewAttendence()),);

                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Complaint Reply '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewComplaintReply()),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Internal Mark '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewInternalMark()),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Question Paper '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewQuestionPaper()),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Study Material '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewStudyMaterials()),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Subject'),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewSubject()),);
                },
              // ),ListTile(
              //   leading: const Icon(Icons.edit),
              //   title: const Text(' View Subject Teacher '),
              //   onTap: () {
              //     Navigator.pop(context);
              //     Navigator.push(
              //       context,
              //       MaterialPageRoute(builder: (context) => ViewSubjectTeacher()),);
              //   },
              // ),ListTile(
              //   leading: const Icon(Icons.edit),
              //   title: const Text(' View Tutor '),
              //   onTap: () {
              //     Navigator.pop(context);
              //     Navigator.push(
              //       context,
              //       MaterialPageRoute(builder: (context) => ViewTutor()),);
              //   },
              ),
              ListTile(
                leading: const Icon(Icons.logout),
                title: const Text('LogOut'),
                onTap: () {
                  Navigator.pop(context);
                  // Navigator.push(
                  //   context,
                  //   MaterialPageRoute(builder: (context) => ViewTutor()),);
                },
              ),
            ],
          ),
        ),

      ),
    );
  }



  String name_="";
  String email_="";
  String phone_="";
  String place_="";
  String department_="";
  String photo_="";

  void _send_data() async{



    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    String img_url = sh.getString('imageurl').toString();
    String lid = sh.getString('lid').toString();

    final urls = Uri.parse('$url/student_viewtutor_home/');
    try {
      final response = await http.post(urls, body: {
        'lid':lid



      });
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        if (status=='ok') {
          String name=jsonDecode(response.body)['name'].toString();
          String email=jsonDecode(response.body)['email'].toString();
          String phone=jsonDecode(response.body)['phone'].toString();
          String place=jsonDecode(response.body)['place'].toString();
          String department=jsonDecode(response.body)['department'].toString();
          String photo=img_url+jsonDecode(response.body)['photo'].toString();
          print(photo);
          setState(() {

            name_= name;
            email_= email;
            phone_= phone;
            place_= place;
            department_= department;
            photo_= photo;
          });





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


