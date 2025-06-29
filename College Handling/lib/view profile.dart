import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:fluttertoast/fluttertoast.dart';

import 'package:shared_preferences/shared_preferences.dart';

import 'editprofile.dart';

void main() {
  runApp(const ViewProfile());
}

class ViewProfile extends StatelessWidget {
  const ViewProfile({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'View Profile',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const ViewProfilePage(title: 'View Profile'),
    );
  }
}

class ViewProfilePage extends StatefulWidget {
  const ViewProfilePage({super.key, required this.title});

  final String title;

  @override
  State<ViewProfilePage> createState() => _ViewProfilePageState();
}

class _ViewProfilePageState extends State<ViewProfilePage> {

  _ViewProfilePageState()
  {
    _send_data();
  }
  @override
  Widget build(BuildContext context) {



    return WillPopScope(
      onWillPop: () async{ return true; },
      child: Scaffold(
        appBar: AppBar(
          leading: BackButton( ),
          backgroundColor: Theme.of(context).colorScheme.primary,
          title: Text(widget.title),
        ),
        body: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[


              CircleAvatar( backgroundImage:NetworkImage(photo_),
              radius: 50,),
              Column(
                children: [
                  // Image(image: NetworkImage(photo_),height: 200,width: 200,),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(name_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(dob_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(gender_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(email_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(phone_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(address_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(semester_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(course_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(gurdian_name_),
                  ),
                  Padding(
                    padding: EdgeInsets.all(5),
                    child: Text(gurdian_relation_),
                  ),

                ],
              ),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(
                    builder: (context) => EditProfilePage(title: "Edit Profile"),));
                },
                child: Text("Edit Profile"),
              ),

            ],
          ),
        ),

      ),
    );
  }



  String name_="";
  String dob_="";
  String gender_="";
  String email_="";
  String phone_="";
  String address_="";
  String semester_="";
  String course_="";
  String gurdian_name_="";
  String gurdian_relation_="";
  String photo_="";

  void _send_data() async{



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
          String name=jsonDecode(response.body)['name'].toString();
          String dob=jsonDecode(response.body)['dob'].toString();
          String gender=jsonDecode(response.body)['gender'].toString();
          String email=jsonDecode(response.body)['email'].toString();
          String phone=jsonDecode(response.body)['phone'].toString();
          String address=jsonDecode(response.body)['address'].toString();
          String semester=jsonDecode(response.body)['semester'].toString();
          String course=jsonDecode(response.body)['course'].toString();
          String gurdian_name=jsonDecode(response.body)['gurdian_name'].toString();
          String photo=img_url+jsonDecode(response.body)['photo'].toString();
          String gurdian_relation=jsonDecode(response.body)['gurdian_relation'].toString();
 print(photo);
          setState(() {

            name_= name;
            dob_= dob;
            gender_= gender;
            email_= email;
            phone_= phone;
            address_= address;
            semester_= semester;
            course_= course;
            gurdian_name_= gurdian_name;
            photo_= photo;
            gurdian_relation_= gurdian_relation;
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
