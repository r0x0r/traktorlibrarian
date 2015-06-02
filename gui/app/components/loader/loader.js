angular.module('librarian')
    .directive('loader', function () {
      'use strict';

        return {
            scope: {
                message: '='
            },
            restrict: 'E',
            templateUrl: '/static/app/loader/loader.html',
            link: function($scope) {
                console.log($scope.message);
            }
        };
    });
