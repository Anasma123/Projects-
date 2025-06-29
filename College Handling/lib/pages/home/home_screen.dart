import 'dart:convert';
import 'package:http/http.dart' as http;

import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:studybuddy/constants/colors.dart';
import 'package:studybuddy/editprofile.dart';
import 'package:studybuddy/pages/home/stars_screen.dart';


import '../../Change passwoard.dart';
import '../../Doubt clearance.dart';
import '../../Send complaint.dart';
import '../../View announcment.dart';
import '../../View assingment status.dart';
import '../../View assingment.dart';
import '../../View attendence.dart';
import '../../View complaint reply.dart';
import '../../View question paper.dart';
import '../../View study materials.dart';
import '../../View subject.dart';
import '../../view internal mark.dart';
import '../../view profile.dart';
import '../../viewdowt.dart';
import '../../viewnotifications.dart';
import '../login/login_screen.dart';
import 'create_order_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<StatefulWidget> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {


  @override
  void initState() {
    super.initState();
    _send_data();
     viewdata();
  }

  int _selectedIndex = 0;
  static const TextStyle optionStyle = TextStyle(fontSize: 30, fontWeight: FontWeight.bold);
  static const List<Widget> _widgetOptions = <Widget>[
    StarsScreen(),
    CreateOrderScreen(),
    Text(
      'Index 2: Pay',
      style: optionStyle,
    ),
    Text(
      'Index 3: Location',
      style: optionStyle,
    ),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          backgroundColor: Colors.white,
          centerTitle: false,
          // titleSpacing:20,
          // leadingWidth:50,
          title:Text("STUDY BUDDY",style: TextStyle(fontWeight: FontWeight.bold),),
          actions: [
            InkWell(
              onTap: () {
                Navigator.push(context, MaterialPageRoute(builder: (context) => ViewnotificationPage(title: '',),));

              },
              child: SvgPicture.asset(
                'assets/icon/notification_bell_icon.svg',
              ),
            ),
            const SizedBox(width: 10),
            // InkWell(
            //   onTap: () {},
            //   child: SvgPicture.asset(
            //     'assets/icon/three_dots_icon.svg',
            //   ),
            // ),
            const SizedBox(width: 20),
          ],
        ),
        drawer: Drawer(
          child: ListView(

            padding: const EdgeInsets.all(0),
            children: [
               DrawerHeader(

                decoration: BoxDecoration(
                  color: Colors.green,
                ), //BoxDecoration
                child: UserAccountsDrawerHeader(
                  decoration: BoxDecoration(color: Colors.green),
                  accountName: Text(
                    sname_,
                    style: TextStyle(fontSize: 18),
                  ),
                  margin: EdgeInsets.only(top: 1),
                  accountEmail: Text(semail_),
                  currentAccountPictureSize: Size.square(50),
                  currentAccountPicture: CircleAvatar(
                    // backgroundColor: Color.fromARGB(255, 165, 255, 137),
                    // child: Text(
                    //   "A",
                    //   style: TextStyle(fontSize: 30.0, color: Colors.blue),
                    // ), //Text
                    backgroundImage: NetworkImage(sphoto_),
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
                    MaterialPageRoute(builder: (context) => MyChangePasswordPage(title: '',)),);

                },
              ),
              // ListTile(
              //   leading: const Icon(Icons.workspace_premium),
              //   title: const Text(' Chat With Teachers '),
              //   onTap: () {
              //     Navigator.pop(context);
              //     // Navigator.push(
              //     //   context,
              //     //   MaterialPageRoute(builder: (context) => ()),);
              //   },
              // ),
              // ListTile(
              //   leading: const Icon(Icons.video_label),
              //   title: const Text(' Doubt Clearans '),
              //   onTap: () {
              //     Navigator.pop(context);
              //     Navigator.push(
              //       context,
              //       MaterialPageRoute(builder: (context) => DowbtClearnessPage(title: '',)),);
              //   },
              // ),
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' Edit Profile '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => EditProfilePage(title: '',)),);
                },
              ),
              ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' Send Complaint'),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,

                    MaterialPageRoute(builder: (context) => SendComplaintPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Announcment '),
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
                    MaterialPageRoute(builder: (context) => ViewAssingmentPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Assingment Status '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewAssingmentStatusPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' view subject Attendence '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewAttendencePage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Complaint Reply '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewComplaintReplyPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Internal Mark '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewInternalMarkPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Question Paper '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewQuestionPaperPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Study Material '),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewStudyMaterialsPage(title: '',)),);
                },
              ),ListTile(
                leading: const Icon(Icons.edit),
                title: const Text(' View Subject'),
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => ViewSubjectPage(title: '',)),);
                },
                ),ListTile(
                  leading: const Icon(Icons.edit),
                  title: const Text(' View doubt reply '),
                  onTap: () {
                    Navigator.pop(context);
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => student_dowtreply(title: '',)),);
                  },
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
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => LoginScreen()),);
                },
              ),
            ],
          ),
        ),

        body:
        Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Container(
                height: 200,
                decoration: BoxDecoration(
                    color: Colors.amber[200],
                    borderRadius: BorderRadius.circular(20)
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    CircleAvatar(
                      backgroundImage: NetworkImage(sphoto_),
                      radius: 60,
                    ),
                    Padding(
                      padding: const EdgeInsets.only(right: 70,top: 50),
                      child: Container(
                        width: 150,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [

                            Text(sname_,style: TextStyle(fontWeight:FontWeight.bold),),
                            Text(sphone_,style: TextStyle(fontWeight:FontWeight.bold),),
                            Text(semail_,style: TextStyle(fontWeight:FontWeight.bold),),
                            Text(scourse_,style: TextStyle(fontWeight:FontWeight.bold),),
                            Text('sem :  '+ssemester_,style: TextStyle(fontWeight:FontWeight.bold),),
                            Text('attendence : '+total_,style: TextStyle(fontWeight:FontWeight.bold),),
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

                  maxCrossAxisExtent: 410,
                  mainAxisExtent: 210,
                  childAspectRatio: 10/10,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,


                ),
                padding: const EdgeInsets.all(8.0),
                children: [
                  InkWell(
                    onTap: () async {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => ViewSubjectPage(title: '')),);
                    },
                    child: Container(
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                            color: Color.fromARGB(255, 18, 82, 98),
                            borderRadius: BorderRadius.circular(15)),
                        child:  Column(
                            children: [
                              SizedBox(height: 5.0),
                              CircleAvatar(
                                  radius: 50,
                                  backgroundImage: AssetImage("assets/images/subject.png")),
                              // SizedBox(height: 5.0),
                              // CircleAvatar(radius: 50,backgroundImage: AssetImage("f.png")),
                              Column(
                                children: [
                                  Padding(
                                    padding: EdgeInsets.all(1),
                                    child: Text("View subject",style: TextStyle(color: Colors.white,fontSize: 18)),
                                  ),],
                              ),
                              Column(
                                children: [
                                  Padding(
                                    padding: EdgeInsets.all(2),
                                    child: Text("Chat",style: TextStyle(color: Colors.white)),
                                  ),],
                              ),
                              Column(
                                children: [
                                  Padding(
                                    padding: EdgeInsets.all(1),
                                    child: Text("Doubt",style: TextStyle(color: Colors.white)),
                                  ),
                                ],
                              ),


                            ]
                        )
                    ),
                  ),
                  InkWell(
                    onTap: () async {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => ViewAssingmentPage(title: '')),);
                    },
                    child: Container(
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                            color: Color.fromARGB(255, 18, 82, 98),
                            borderRadius: BorderRadius.circular(15)),
                        child:  Column(
                            children: [
                              SizedBox(height: 5.0),
                              CircleAvatar(
                                  radius: 50,
                                  backgroundImage: AssetImage("assets/images/assingment.jpg")),
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
                                    child: Text("View Your Assingmnets",style: TextStyle(color: Colors.white,fontSize: 18)),
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
                    ),
                  ),
                  InkWell(
                    onTap: () async {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => ViewAttendencePage(title: '')),);
                    },
                    child: Container(
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                            color: Color.fromARGB(255, 18, 82, 98),
                            borderRadius: BorderRadius.circular(15)),
                        child:  Column(
                            children: [
                              SizedBox(height: 5.0),
                              CircleAvatar(
                                  radius: 50,backgroundImage: AssetImage("assets/images/att.png")),
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
                                    child: Text("View Your Attendence",style: TextStyle(color: Colors.white,fontSize: 18)),
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
                    ),
                  ),
                  InkWell(
                    onTap: () async {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => ViewAnnouncementPage(title: '')),);
                    },
                    child: Container(
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                            color: Color.fromARGB(255, 18, 82, 98),
                            borderRadius: BorderRadius.circular(15)),
                        child:  Column(
                            children: [
                              SizedBox(height: 5.0),
                              CircleAvatar(
                                  radius: 50,backgroundImage: AssetImage("assets/images/ann.jpg")),
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
                                    child: Text("View Announcment",style: TextStyle(color: Colors.white,fontSize: 18)),
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
                    ),
                  ),
                  InkWell(
                    onTap: () async {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => ViewStudyMaterialsPage(title: '')),);
                    },
                    child: Container(
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                            color: Color.fromARGB(255, 18, 82, 98),
                            borderRadius: BorderRadius.circular(15)),
                        child:  Column(
                            children: [
                              SizedBox(height: 5.0),
                              CircleAvatar(
                                  radius: 50,backgroundImage: AssetImage("assets/images/ss.png")),
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
                                    child: Text("View Study Materials",style: TextStyle(color: Colors.white,fontSize: 18)),
                                  ),
                                ],
                              ),


                            ]
                        )
                    ),
                  ),
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
                ],


              ),
            ),


          ],
        ),

    // bottomNavigationBar: Container(
    //         decoration: const BoxDecoration(
    //           borderRadius: BorderRadius.only(topRight: Radius.circular(30), topLeft: Radius.circular(30)),
    //           boxShadow: [
    //             BoxShadow(color: Colors.black38, spreadRadius: 0, blurRadius: 10),
    //           ],
    //         ),
    //         child: ClipRRect(
    //           borderRadius: const BorderRadius.only(
    //             topLeft: Radius.circular(30.0),
    //             topRight: Radius.circular(30.0),
    //           ),
    //           child: BottomNavigationBar(
    //             showSelectedLabels: false,
    //             selectedFontSize: 0,
    //             showUnselectedLabels: false,
    //             type: BottomNavigationBarType.fixed,
    //             items: <BottomNavigationBarItem>[
    //               // BottomNavigationBarItem(
    //               //     icon: SvgPicture.asset(
    //               //       'assets/icon/u_star.svg',
    //               //       color: _selectedIndex == 0 ? AppColors.mainGreen : AppColors.grey,
    //               //     ),
    //               //     label: ''),
    //               BottomNavigationBarItem(
    //                 icon: SvgPicture.asset(
    //                   'assets/icon/u_cup.svg',
    //                   color: _selectedIndex == 1 ? AppColors.mainGreen : AppColors.grey,
    //                 ),
    //                 label: '',
    //               ),
    //               BottomNavigationBarItem(
    //                   icon: SvgPicture.asset(
    //                     'assets/icon/u_credit-card.svg',
    //                     color: _selectedIndex == 2 ? AppColors.mainGreen : AppColors.grey,
    //                   ),
    //                   label: ''),
    //               BottomNavigationBarItem(
    //                   icon: SvgPicture.asset(
    //                     'assets/icon/u_location-point.svg',
    //                     color: _selectedIndex == 3 ? AppColors.mainGreen : AppColors.grey,
    //                   ),
    //                   label: ''),
    //             ],
    //             currentIndex: _selectedIndex,
    //             selectedItemColor: Colors.amber[800],
    //             onTap: _onItemTapped,
    //           ),
    //         ),
    //         ),
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


  String sname_="";
  String sdob_="";
  String sgender_="";
  String semail_="";
  String sphone_="";
  String saddress_="";
  String ssemester_="";
  String scourse_="";
  String sgurdian_name_="";
  String sgurdian_relation_="";
  String sphoto_="";
  String total_="";
  void viewdata() async{



    SharedPreferences sh = await SharedPreferences.getInstance();
    String url = sh.getString('url').toString();
    String img_url = sh.getString('imageurl').toString();
    String lid = sh.getString('lid').toString();

    final urls = Uri.parse('$url/student_profile/');
    try {
      final response = await http.post(urls, body: {
        'lid':lid



      });
      if (response.statusCode == 200) {
        String status = jsonDecode(response.body)['status'];
        if (status=='ok') {
          String sname=jsonDecode(response.body)['name'].toString();
          String sdob=jsonDecode(response.body)['dob'].toString();
          String sgender=jsonDecode(response.body)['gender'].toString();
          String semail=jsonDecode(response.body)['email'].toString();
          String sphone=jsonDecode(response.body)['phone'].toString();
          String saddress=jsonDecode(response.body)['address'].toString();
          String ssemester=jsonDecode(response.body)['semester'].toString();
          String scourse=jsonDecode(response.body)['course'].toString();
          String sgurdian_name=jsonDecode(response.body)['gurdian_name'].toString();
          String sphoto=img_url+jsonDecode(response.body)['photo'].toString();
          String sgurdian_relation=jsonDecode(response.body)['gurdian_relation'].toString();
          String total=jsonDecode(response.body)['total'].toString();
          print(sphoto);
          setState(() {

            sname_= sname;
            sdob_= sdob;
            sgender_= sgender;
            semail_= semail;
            sphone_= sphone;
            saddress_= saddress;
            ssemester_= ssemester;
            scourse_= scourse;
            sgurdian_name_= sgurdian_name;
            sphoto_= sphoto;
            sgurdian_relation_= sgurdian_relation;
            total_= total;
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
