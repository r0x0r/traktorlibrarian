/*global $:false */
/*global angular:false */
/*global console:false */

angular.module('librarian', ['ngRoute'])

.config(['$routeProvider',
        function($routeProvider)  {
          'use strict';

    $routeProvider
        .when('/clean/', {
            templateUrl: '../static/components/clean/clean.html',
            controller: 'CleanController'
        })
        .when('/export', {
            templateUrl: '../static/components/export/export.html',
            controller: 'ExportController'
        })
        .when('/', {
            templateUrl: '../static/components/landing/landing.html',
            controller: 'LandingController'
        });
        }]);
